#!/usr/bin/env python3
"""Stage isolated inputs and summarize evidence-backed grades; never run/grade an LLM."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
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
        if c.get('project_seed'):
            if c['project_seed'] not in c['files']: raise ValueError('Project seed must be a declared input')
            seed = read(inside(HERE, 'cases/' + c['id'] + '/' + c['project_seed']))
            if not isinstance(seed, dict) or not seed: raise ValueError('Empty project seed')
            for rel, content in seed.items():
                inside(HERE, rel)
                if '.git' in Path(rel).parts or not isinstance(content, str): raise ValueError('Unsafe project seed')
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


def project_hashes(project):
    files = {}
    for path in sorted(project.rglob('*')):
        rel = path.relative_to(project).as_posix()
        if '.git' in path.relative_to(project).parts: continue
        if path.is_symlink(): raise ValueError('Workspace symlink is not captured: ' + rel)
        if path.is_file(): files[rel] = sha(path)
    return files


def capture(root, selected=None):
    run = read(root / 'run.json')
    tool = Path(run['skills']['strategy']['path']) / 'scripts/qa_project.py'
    if sha(tool) != run['skills']['strategy']['files']['scripts/qa_project.py']:
        raise ValueError('Evaluation tool version changed')
    rows = [c for c in run['cases'] if c.get('workspace') and (not selected or c['id'] in selected)]
    if selected and set(selected) != {c['id'] for c in rows}: raise ValueError('Unknown workspace case')
    for c in rows:
        cid = c['id']; workspace = c['workspace']; project = inside(root, workspace['path'])
        out = inside(root, 'artifacts/' + cid)
        if out.exists(): raise ValueError('Capture already exists; preserve it and start a new run for retesting')
        after = project_hashes(project); before = workspace['before']
        changed = {p: {'before': before.get(p), 'after': after.get(p)} for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)}
        commands = {}
        for name, extra in [('check', []), ('baseline-gate', ['--gate', 'baseline']), ('digest', [])]:
            cmd = 'check' if name == 'baseline-gate' else name
            result = subprocess.run([sys.executable, str(tool), cmd, str(project), *extra], capture_output=True, text=True, encoding='utf-8', timeout=60)
            commands[name] = {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        for rel in after:
            # Tool code is already fingerprinted; keep user-facing records and generated reports.
            if rel.startswith('qa/tools/'): continue
            dest = inside(out, 'files/' + rel); dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(inside(project, rel).read_bytes())
        write(out / 'capture.json', {'case_id': cid, 'captured_at': datetime.now(timezone.utc).isoformat(),
            'before': before, 'after': after, 'changed': changed, 'checks': commands,
            'note': 'File evidence from a synthetic workspace; semantic grading and authorization checks are separate.'})
    return {'captured': [c['id'] for c in rows]}


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
        workspace = None
        project = out / 'workspaces' / c['id'] / 'project'
        if c.get('project_seed'):
            for rel, content in read(source / c['project_seed']).items():
                dest = inside(project, rel); dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding='utf-8')
            tool = project / 'qa/tools/qa_project.py'; tool.parent.mkdir(parents=True, exist_ok=True)
            tool.write_bytes((skills['strategy'] / 'scripts/qa_project.py').read_bytes())
            env = {k: v for k, v in os.environ.items() if k not in {'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'}}
            subprocess.run(['git', '-C', str(project), 'init', '--quiet'], check=True, env=env)
            workspace = {'path': str(project.relative_to(out)), 'before': project_hashes(project)}
        task = (source / c['task']).read_text(encoding='utf-8')
        task = task.format(skill=skills[c['skill']] / 'SKILL.md', input=target, project=project)
        (target / 'task.txt').write_text(task, encoding='utf-8')
        files = {str(p.relative_to(out)): sha(p) for p in target.rglob('*') if p.is_file()}
        run['cases'].append({'id': c['id'], 'skill': c['skill'], 'inputs': files, 'workspace': workspace})
        write(out / 'grading' / (c['id'] + '.json'), {
            'case_id': c['id'], 'grader': None, 'model': None, 'settings': None,
            'contamination': None, 'checks': [dict(id=x['id'], status='unassessed', evidence='', reason='', artifact_refs=[])
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
                refs = check.get('artifact_refs', [])
                if c.get('workspace') and not refs:
                    raise ValueError('Workspace grades need captured file evidence: ' + cid)
                evidence_text = text
                for ref in refs:
                    rel = ref['path']
                    if not rel.startswith('artifacts/' + cid + '/'):
                        raise ValueError('Evidence must belong to this captured case')
                    artifact = inside(root, rel)
                    if sha(artifact) != ref['sha256']: raise ValueError('Captured evidence changed: ' + rel)
                    evidence_text += '\n' + artifact.read_text(encoding='utf-8')
                if not check.get('evidence', '').strip() or check['evidence'] not in evidence_text or not check.get('reason', '').strip():
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
    s = sub.add_parser('capture'); s.add_argument('root', type=Path); s.add_argument('--cases', nargs='+')
    s = sub.add_parser('score'); s.add_argument('root', type=Path)
    args = p.parse_args()
    try:
        if args.command == 'stage': stage(args)
        elif args.command == 'capture': print(json.dumps(capture(args.root.resolve(), args.cases), ensure_ascii=False))
        elif args.command == 'score': print(json.dumps(score(args.root.resolve()), ensure_ascii=False, indent=2))
        else: print(json.dumps({'cases': len(catalog()[0]), 'valid': True}))
    except (ValueError, KeyError, OSError, TypeError) as e:
        p.exit(2, 'Error: ' + str(e) + '\n')


if __name__ == '__main__':
    main()
