import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('evaluate', Path(__file__).with_name('evaluate.py'))
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


class EvaluationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.skill = self.base / 'skill'
        self.skill.mkdir()
        (self.skill / 'SKILL.md').write_text('fixture skill', encoding='utf-8')
        self.out = self.base / 'run'

    def stage(self):
        ev.stage(argparse.Namespace(out=self.out, strategy=self.skill, review=self.skill, cases=['case-01']))

    def grade(self, status='pass'):
        (self.out / 'responses' / 'case-01.md').write_text('Observed response: equal is unresolved.', encoding='utf-8')
        path = self.out / 'grading' / 'case-01.json'
        g = ev.read(path)
        g.update(grader='test evaluator', model='unknown', settings='unknown', contamination=False)
        for check in g['checks']:
            check.update(status=status, evidence='equal is unresolved.', reason='Fixture grade for integrity test only')
        ev.write(path, g)
        return path, g

    def test_inputs_are_isolated_and_missing_run_is_not_pass(self):
        self.stage()
        self.assertEqual({p.name for p in (self.out / 'tasks' / 'case-01').iterdir()}, {'task.txt', 'draft.md'})
        result = ev.score(self.out)
        self.assertEqual(result['counts']['NOT_RUN'], 1)
        self.assertEqual(result['counts']['PASS'], 0)
        self.assertEqual(result['core_total'], 8)
        self.assertEqual(result['selected_total'], 1)

    def test_existing_output_is_never_overwritten(self):
        self.out.mkdir()
        sentinel = self.out / 'notes.txt'
        sentinel.write_text('user work', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'already exists'): self.stage()
        self.assertEqual(sentinel.read_text(), 'user work')

    def test_changed_task_is_rejected(self):
        self.stage()
        (self.out / 'tasks' / 'case-01' / 'draft.md').write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Input changed'): ev.score(self.out)

    def test_grade_requires_real_excerpt_and_all_checks(self):
        self.stage()
        path, grade = self.grade()
        self.assertEqual(ev.score(self.out)['counts']['PASS'], 1)
        grade['checks'][0]['evidence'] = 'not in the response'
        ev.write(path, grade)
        with self.assertRaisesRegex(ValueError, 'verbatim evidence'): ev.score(self.out)
        grade['checks'].pop()
        ev.write(path, grade)
        with self.assertRaisesRegex(ValueError, 'IDs mismatch'): ev.score(self.out)

    def test_incomplete_fail_and_contamination_are_separate(self):
        self.stage()
        path, grade = self.grade('unassessed')
        self.assertEqual(ev.score(self.out)['counts']['INCOMPLETE'], 1)
        grade['checks'][0]['status'] = 'fail'
        ev.write(path, grade)
        self.assertEqual(ev.score(self.out)['counts']['FAIL'], 1)
        grade['contamination'] = True
        ev.write(path, grade)
        self.assertEqual(ev.score(self.out)['counts']['CONTAMINATED'], 1)

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError): ev.inside(self.base, '../outside')
        with self.assertRaises(ValueError): ev.inside(self.base, str(self.base.absolute()))


if __name__ == '__main__':
    unittest.main()
