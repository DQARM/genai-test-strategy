#!/usr/bin/env python3
"""Stage isolated inputs and summarize evidence-backed grades; never run/grade an LLM."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe relative path: ' + str(relative))
    candidate = root / p
    if any(x.is_symlink() for x in [candidate, *candidate.parents] if x != root.parent):
        raise ValueError('Symlink not allowed: ' + str(relative))
    candidate.resolve().relative_to(root.resolve())
    return candidate


def catalog():
    suite, rubrics = read(HERE / 'suite.json'), read(HERE / 'rubrics.json')
    cases = suite['cases']
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)) or set(ids) != set(rubrics):
        raise ValueError('Case and rubric IDs must match without duplicates')
    for c in cases:
        files = [c['task'], *c['files']]
        if c['skill'] not in {'strategy', 'review'} or len(files) != len(set(files)):
            raise ValueError('Invalid task definition')
        for name in files:
            inside(HERE, 'cases/' + c['id'] + '/' + name).read_text(encoding='utf-8')
        checks = rubrics[c['id']]['checks']
        if not checks or len({x['id'] for x in checks}) != len(checks):
            raise ValueError('Checks must be nonempty and unique')
    return cases, rubrics


def skill_fingerprint(path):
    path = path.resolve()
    if not (path / 'SKILL.md').is_file():
        raise ValueError('Actual skill directory required: ' + str(path))
    files = [path / 'SKILL.md']
    for sub in ('references', 'scripts'):
        files += sorted(p for p in (path / sub).rglob('*') if p.is_file() and p.suffix in {'.md', '.py'})
    return {'path': str(path), 'files': {str(p.relative_to(path)): sha(p) for p in files}}


def stage(args):
    cases, rubrics = catalog()
    wanted = args.cases or [c['id'] for c in cases]
    if len(wanted) != len(set(wanted)) or set(wanted) - {c['id'] for c in cases}:
        raise ValueError('Unknown or duplicate selected case')
    out = args.out.absolute()
    # Do not materialize test data inside an installed skill or overwrite another run.
    skills = {'strategy': args.strategy.resolve(), 'review': args.review.resolve()}
    for path in skills.values():
        if out.resolve() == path or path in out.resolve().parents:
            raise ValueError('Evaluation output must be outside the skill directories')
    versions = {k: skill_fingerprint(v) for k, v in skills.items()}
    if out.exists() or out.is_symlink():
        raise ValueError('Output already exists; use a fresh run directory')
    # Validate all inputs before creating output.
    out.mkdir(parents=True)
    run = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
           'rubric_sha256': sha(HERE / 'rubrics.json'), 'suite_sha256': sha(HERE / 'suite.json'),
           'skills': versions, 'core_case_ids': [c['id'] for c in cases], 'cases': []}
    (out / 'responses').mkdir()
    for c in cases:
        if c['id'] not in wanted:
            continue
        target = out / 'tasks' / c['id']
        target.mkdir(parents=True)
        source = HERE / 'cases' / c['id']
        for name in c['files']:
            dest = inside(target, name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(inside(source, name).read_bytes())
        task = (source / c['task']).read_text(encoding='utf-8')
        task = task.format(skill=skills[c['skill']] / 'SKILL.md', input=target)
        (target / 'task.txt').write_text(task, encoding='utf-8')
        files = {str(p.relative_to(out)): sha(p) for p in target.rglob('*') if p.is_file()}
        run['cases'].append({'id': c['id'], 'skill': c['skill'], 'inputs': files})
        write(out / 'grading' / (c['id'] + '.json'), {
            'case_id': c['id'], 'grader': None, 'model': None, 'settings': None,
            'contamination': None, 'checks': [dict(id=x['id'], status='unassessed', evidence='', reason='')
                                            for x in rubrics[c['id']]['checks']]})
    write(out / 'run.json', run)
    print(json.dumps({'run': str(out), 'tasks': [str(out / 'tasks' / c['id'] / 'task.txt') for c in run['cases']]}, ensure_ascii=False))


def score(root):
    run = read(root / 'run.json')
    cases, rubrics = catalog()
    if run.get('rubric_sha256') != sha(HERE / 'rubrics.json') or run.get('suite_sha256') != sha(HERE / 'suite.json'):
        raise ValueError('Suite/rubric changed; use the original version or start a new run')
    selected = [c['id'] for c in run['cases']]
    core_ids = [c['id'] for c in cases]
    if len(selected) != len(set(selected)) or set(selected) - set(core_ids) or run['core_case_ids'] != core_ids:
        raise ValueError('Invalid run case list')
    rows = []
    for c in run['cases']:
        for path, digest in c['inputs'].items():
            if sha(inside(root, path)) != digest:
                raise ValueError('Input changed: ' + path)
        cid = c['id']
        transcript = inside(root, 'responses/' + cid + '.md')
        grade_path = inside(root, 'grading/' + cid + '.json')
        if not transcript.is_file() or not grade_path.is_file():
            rows.append({'id': cid, 'outcome': 'NOT_RUN'}); continue
        text = transcript.read_text(encoding='utf-8')
        grade = read(grade_path)
        checks = grade.get('checks', [])
        expected = {x['id'] for x in rubrics[cid]['checks']}
        if grade.get('case_id') != cid or {x.get('id') for x in checks} != expected or len(checks) != len(expected):
            raise ValueError('Grade check IDs mismatch: ' + cid)
        statuses = []
        for check in checks:
            status = check.get('status')
            if status not in {'pass', 'fail', 'unassessed'}:
                raise ValueError('Invalid check status: ' + cid)
            if status != 'unassessed':
                if not check.get('evidence', '').strip() or check['evidence'] not in text or not check.get('reason', '').strip():
                    raise ValueError('Grade needs verbatim evidence and reasoning: ' + cid)
            statuses.append(status)
        assessed = any(x != 'unassessed' for x in statuses)
        if assessed and (any(not isinstance(grade.get(k), str) or not grade[k].strip() for k in ('grader', 'model', 'settings'))
                         or not isinstance(grade.get('contamination'), bool)):
            raise ValueError('Missing grader/model/settings/contamination: ' + cid)
        outcome = 'FAIL' if 'fail' in statuses else ('PASS' if all(x == 'pass' for x in statuses) else 'INCOMPLETE')
        if grade.get('contamination') is True:
            outcome = 'CONTAMINATED'
        rows.append({'id': cid, 'outcome': outcome, 'transcript_sha256': sha(transcript),
                     'checks': {s: statuses.count(s) for s in ('pass', 'fail', 'unassessed')}})
    counts = {s: sum(x['outcome'] == s for x in rows) for s in ('PASS', 'FAIL', 'INCOMPLETE', 'NOT_RUN', 'CONTAMINATED')}
    return {'core_total': len(core_ids), 'selected_total': len(selected),
            'not_selected': [x for x in core_ids if x not in selected], 'counts': counts, 'cases': rows,
            'note': 'Evidence linkage and evaluator grades only; not automatic semantic validation or product test results.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('check-suite')
    s = sub.add_parser('stage')
    s.add_argument('--out', type=Path, required=True)
    s.add_argument('--strategy', type=Path, required=True)
    s.add_argument('--review', type=Path, required=True)
    s.add_argument('--cases', nargs='+')
    s = sub.add_parser('score'); s.add_argument('root', type=Path)
    args = p.parse_args()
    try:
        if args.command == 'stage': stage(args)
        elif args.command == 'score': print(json.dumps(score(args.root.resolve()), ensure_ascii=False, indent=2))
        else: print(json.dumps({'cases': len(catalog()[0]), 'valid': True}))
    except (ValueError, KeyError, OSError, TypeError) as e:
        p.exit(2, 'Error: ' + str(e) + '\n')


if __name__ == '__main__':
    main()
