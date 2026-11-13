"""Regression checks using synthetic projects and approvals; never product evidence."""
import hashlib
import copy
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

TOOL = Path(__file__).with_name("qa_project.py")


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def get(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReportParser(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids, self.links, self.records, self.scripts = [], [], {}, []
        self.current = None
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'article' and 'data-record-id' in attrs:
            self.current = attrs['data-record-id']
            self.records[self.current] = {'anchor': attrs['id'], 'links': [], 'text': ''}
        if tag == 'a':
            href = attrs.get('href', '')
            self.links.append(href)
            if self.current:
                self.records[self.current]['links'].append(href)
        if tag == 'script':
            self.scripts.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'article':
            self.current = None

    def handle_data(self, data):
        if self.current:
            self.records[self.current]['text'] += data


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qa-test-")
        self.root = Path(self.temp.name) / "專案 with spaces"
        self.run_tool("init", "--name", "Synthetic fixture")

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, command, *args, ok=True, root=None):
        p = subprocess.run([sys.executable, str(TOOL), command, str(root or self.root), *args],
                           capture_output=True, text=True, encoding="utf-8",
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if ok:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, check=True)
        return p.stdout.decode()

    def fixture(self):
        root = self.root
        (root / "inputs").mkdir()
        (root / "inputs/spec.md").write_text("Synthetic test rule: after evaluate, output ON.\n", encoding="utf-8")
        (root / "inputs/harness.md").write_text("Synthetic harness: reset, evaluate, inspect output; isolated state.\n", encoding="utf-8")
        (root / "qa/decisions/DEC-001.md").write_text("Synthetic approval fixture for tool regression tests only.\n", encoding="utf-8")
        confirm = {"by": "synthetic-fixture-owner", "at": "2026-11-09T00:00:00Z", "evidence_ref": "qa/decisions/DEC-001.md"}
        reg = get(root / "qa/registry.json")
        reg["scope"] = {"objective": "Check synthetic output", "in": ["module"], "out": ["physical device"],
                        "selected_ac_ids": ["AC-001"], "selected_risk_ids": ["RISK-001"],
                        "selected_scenario_ids": ["SC-001"], "selected_case_ids": ["TC-001"], "decision_ref": "DEC-001"}
        reg["sources"] = [{"id": sid, "path": path, "sha256": sha(root / path), "locator": "whole file", "kind": kind,
                           "status": "confirmed"} for sid, path, kind in
                          [("SRC-SPEC", "inputs/spec.md", "normative"), ("SRC-HARNESS", "inputs/harness.md", "harness")]]
        reg["decisions"] = [{"id": "DEC-001", "statement": "Synthetic adoption", **confirm}]
        rule = {"id": "REQ-001", "text": "Output must be ON after evaluate", "revision": 1, "status": "confirmed",
                "source_refs": ["SRC-SPEC"], "decision_refs": ["DEC-001"], "confirmation": confirm}
        reg["requirements"] = [rule]
        reg["acceptance"] = [{**rule, "id": "AC-001", "requirement_ids": ["REQ-001"],
                              "oracle": {"observe": "output", "when": "after evaluate", "tolerance": "exact"}}]
        reg["project"]["risk_criteria"] = {"status": "confirmed", "decision_refs": ["DEC-001"],
            "severity": {"high": "Synthetic main function lost", "low": "Synthetic cosmetic effect"},
            "likelihood": {"high": "Observed often in synthetic fixture", "low": "Rare in synthetic fixture"},
            "priority": {"P1": "Selected synthetic scope", "P2": "Later synthetic scope"}}
        rule["risk_assessment"] = {"status": "confirmed", "requirement_revision": 1,
            "rationale": "Synthetic assessment of missing control", "decision_refs": ["DEC-001"]}
        reg["risks"] = [{"id": "RISK-001", "failure": "OFF after evaluate", "impact": "control lost",
                         "requirement_ids": ["REQ-001"], "severity": "high", "severity_rationale": "Main output unavailable",
                         "likelihood": "unknown", "likelihood_rationale": "No field data",
                         "uncertainty": "high", "priority": "P1", "rationale": "selected promise",
                         "source_refs": ["SRC-SPEC"]}]
        reg["scenarios"] = [{"id": "SC-001", "description": "Evaluate from OFF", "category": "state",
                             "ac_ids": ["AC-001"], "risk_ids": ["RISK-001"], "selection": "keep", "reason": "risk selected"}]
        reg["coverage_items"] = [{"id": "COV-001", "ac_ids": ["AC-001"], "technique": "state-transition",
                                   "description": "OFF -> evaluate -> ON", "selection": "keep", "reason": "selected transition"}]
        put(root / "qa/registry.json", reg)
        case = {"id": "TC-001", "title": "Evaluate changes OFF to ON", "revision": 1, "status": "ready",
                "purpose": "Detect missing output", "level": "unit", "type": "manual", "ac_ids": ["AC-001"],
                "risk_ids": ["RISK-001"], "scenario_ids": ["SC-001"], "coverage_ids": ["COV-001"],
                "environment": {"target": "isolated fixture", "build_binding": "record fixture version at run", "tools": "fixture v1", "binding_refs": ["SRC-HARNESS"]},
                "preconditions": [{"action": "reset fixture to OFF", "verify": "read output OFF"}],
                "data": [{"name": "initial", "value": "OFF", "unit": "discrete", "basis": "SRC-HARNESS"}],
                "steps": [{"n": 1, "action": "evaluate once", "input": "OFF", "observe": "output", "when": "on return", "evidence": "capture fixture JSON",
                           "checks": [{"expected": "output ON", "rule_refs": ["AC-001"], "coverage_ids": ["COV-001"]}]}],
                "cleanup": [{"action": "close fixture", "verify": "process terminated"}], "independence": "fresh process each case",
                "verdict_rules": {"pass": "ON", "fail": "not ON with valid input", "inconclusive": "no output"}, "blockers": []}
        put(root / "qa/cases/TC-001.json", case)
        self.run_tool("check")
        artifact = self.run_tool("digest").stdout.strip()
        put(root / "qa/reviews/REV-001.json", {"id": "REV-001", "artifact_digest": artifact,
            "reviewer": "synthetic-reviewer", "session": "synthetic-session", "at": "2026-11-09T00:01:00Z",
            "independence": "human", "rounds": ["traceability", "executable", "coverage", "consistency"], "findings": []})
        put(root / "qa/approvals/APP-001.json", {**confirm, "artifact_digest": artifact, "case_ids": ["TC-001"]})
        return reg, case

    def refresh_review(self):
        # Synthetic approval fixtures only, after an intentional test-data change.
        artifact = self.run_tool("digest").stdout.strip()
        for filename in ("qa/reviews/REV-001.json", "qa/approvals/APP-001.json"):
            path = self.root / filename
            data = get(path)
            data["artifact_digest"] = artifact
            put(path, data)

    def charter(self):
        return {"id": "EXP-001", "title": "Observe repeat evaluation", "status": "ready",
                "mission": "Learn behavior where product rule is missing", "scope": ["synthetic isolated fixture"],
                "timebox_minutes": 10, "ac_ids": [], "question_ids": [], "source_refs": ["SRC-HARNESS"],
                "binding_refs": ["SRC-HARNESS"],
                "preconditions": [{"action": "reset fixture", "verify": "read OFF"}],
                "actions": [{"action": "evaluate twice", "observe": "two outputs", "evidence": "record actual JSON"}],
                "stop_conditions": ["timebox ends", "fixture becomes unavailable"],
                "cleanup": [{"action": "close fixture", "verify": "process terminated"}]}

    def qa_pair(self, **changes):
        row = {"id": "QA-001", "kind": "clarification", "question_id": None,
               "question_text": "哪些模式允許匯出？", "options": ["所有模式", "只有維修模式"],
               "answer_text": "第二個", "answer_status": "answered", "capture": "verbatim",
               "missing_reason": None, "asked_at": None, "answered_at": None, "answered_by": "使用者",
               "interpretation": "只有維修模式允許；其餘限制未確認。", "related_ids": [],
               "supersedes": None, "change_reason": None}
        row.update(changes)
        return row

    def record_pair(self, row, ok=True):
        put(self.root / "qa/input.json", row)
        return self.run_tool("record-qa", "--input", "qa/input.json", ok=ok)

    def test_qa_preserves_short_answer_options_and_does_not_create_decisions(self):
        row = self.qa_pair(answer_text="  第二個\n保留原始換行與空白。  ")
        before = get(self.root / "qa/registry.json")
        self.record_pair(row)
        reg = get(self.root / "qa/registry.json")
        stored = reg["interactions"][0]
        self.assertEqual(stored["answer_text"], row["answer_text"])
        self.assertEqual(stored["options"], row["options"])
        self.assertEqual(reg["decisions"], before["decisions"])
        self.assertEqual(reg["questions"], before["questions"])
        self.assertEqual(reg["requirements"], before["requirements"])
        self.assertIsNone(stored["answered_at"])
        self.assertTrue(stored["answer_recorded_at"])
        self.assertEqual(json.loads(self.run_tool("show-qa", "--id", "QA-001").stdout), stored)
        index = self.run_tool("show-qa").stdout
        self.assertNotIn(row["answer_text"], index)
        self.assertNotIn("interpretation", index)

    def test_qa_pending_is_completed_once_without_changing_question(self):
        row = self.qa_pair(answer_status="pending", answer_text=None, answered_by=None, interpretation=None)
        self.record_pair(row)
        saved = get(self.root / "qa/registry.json")["interactions"][0]
        completed = {**saved, "answer_status": "answered", "answer_text": "第二個", "answered_by": "使用者", "interpretation": "僅維修模式"}
        self.record_pair(completed)
        actual = get(self.root / "qa/registry.json")["interactions"]
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0]["recorded_at"], saved["recorded_at"])
        self.assertEqual(actual[0]["question_text"], saved["question_text"])
        self.assertIn("unchanged", self.record_pair(actual[0]).stdout)
        changed = {**actual[0], "answer_text": "第一個"}
        self.assertIn("cannot be overwritten", self.record_pair(changed, ok=False).stderr)
        self.assertEqual(get(self.root / "qa/registry.json")["interactions"], actual)

    def test_qa_pending_cannot_change_options_during_completion(self):
        row = self.qa_pair(answer_status="pending", answer_text=None, answered_by=None, interpretation=None)
        self.record_pair(row)
        before = (self.root / "qa/registry.json").read_bytes()
        completed = self.qa_pair(options=["只有維修模式", "所有模式"])
        self.record_pair(completed, ok=False)
        self.assertEqual((self.root / "qa/registry.json").read_bytes(), before)

    def test_qa_unknown_answer_is_kept_but_cannot_support_a_decision(self):
        reg, _ = self.fixture()
        self.record_pair(self.qa_pair(answer_text="不知道", answer_status="unknown", interpretation="仍未決定，不能推定不允許。"))
        reg = get(self.root / "qa/registry.json")
        reg["decisions"][0]["interaction_refs"] = ["QA-001"]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("cannot support a confirmed decision", self.run_tool("check", ok=False).stdout)
        self.assertEqual(reg["interactions"][0]["answer_text"], "不知道")

    def test_qa_correction_retains_original_and_warns_stale_decision(self):
        self.fixture()
        self.record_pair(self.qa_pair(related_ids=["REQ-001", "RISK-001"]))
        reg = get(self.root / "qa/registry.json")
        old = copy.deepcopy(reg["interactions"][0])
        reg["decisions"][0]["interaction_refs"] = ["QA-001"]
        put(self.root / "qa/registry.json", reg)
        self.record_pair(self.qa_pair(id="QA-002", kind="correction", answer_text="更正，所有模式皆可。",
                                     interpretation="使用者更正為所有模式；受影響規則待更新。",
                                     supersedes="QA-001", change_reason="使用者更正適用模式"))
        current = get(self.root / "qa/registry.json")
        self.assertEqual(current["interactions"][0], old)
        self.assertEqual(len(current["interactions"]), 2)
        self.assertIn("superseded answer QA-001", self.run_tool("check").stdout)
        self.run_tool("render")
        html = (self.root / "qa/report.html").read_text(encoding="utf-8")
        parser = ReportParser(html)
        for rid in ("QA-001", "QA-002"):
            self.assertIn("#" + parser.records[rid]["anchor"], parser.records["TC-001"]["links"])
            self.assertIn("#" + parser.records["TC-001"]["anchor"], parser.records[rid]["links"])
        self.assertIn("已由", parser.records["QA-001"]["text"])
        self.assertIn("#" + parser.records["QA-001"]["anchor"], parser.records["DEC-001"]["links"])
        self.assertIn("#" + parser.records["QA-001"]["anchor"], parser.records["REQ-001"]["links"])
        self.assertIn("#" + parser.records["QA-001"]["anchor"], parser.records["RISK-001"]["links"])

    def test_qa_missing_original_requires_label_and_never_fills_raw_fields(self):
        row = self.qa_pair(capture="summary_only", question_text=None, options=[], answer_text=None,
                           answer_status="unavailable", missing_reason="舊紀錄僅存摘要，原問答已不可見。")
        self.record_pair(row)
        self.assertIn("incomplete original Q&A", self.run_tool("check").stdout)
        saved = get(self.root / "qa/registry.json")["interactions"][0]
        self.assertIsNone(saved["question_text"])
        self.assertIsNone(saved["answer_text"])
        self.record_pair(self.qa_pair(id="QA-002", capture="summary_only"), ok=False)
        self.record_pair(self.qa_pair(id="QA-003", capture="partial", missing_reason=None), ok=False)

    def test_qa_invalid_refs_cycles_and_times_do_not_write_partial_records(self):
        self.record_pair(self.qa_pair())
        before = (self.root / "qa/registry.json").read_bytes()
        for change in ({"related_ids": ["REQ-MISSING"]}, {"question_id": "Q-MISSING"},
                       {"supersedes": "QA-002", "change_reason": "循環"},
                       {"supersedes": "QA-001", "change_reason": None},
                       {"asked_at": "2026-11-13T12:00:00"}, {"options": "第二個"}):
            with self.subTest(change=change):
                self.record_pair(self.qa_pair(id="QA-002", **change), ok=False)
                self.assertEqual((self.root / "qa/registry.json").read_bytes(), before)

    def test_qa_html_escapes_raw_content_and_keeps_all_anchors_valid(self):
        raw = '<script>alert("x")</script> & "第二個"\n```html'
        self.record_pair(self.qa_pair(question_text=raw, answer_text=raw, options=[raw]))
        self.run_tool("render")
        parser = ReportParser((self.root / "qa/report.html").read_text(encoding="utf-8"))
        self.assertFalse(parser.scripts)
        self.assertIn(raw, parser.records["QA-001"]["text"])
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(all(link[1:] in parser.ids for link in parser.links if link.startswith("#")))
        markdown = (self.root / "qa/interview.md").read_text(encoding="utf-8")
        self.assertIn("Question and Answer", markdown)
        self.assertIn("````json", markdown)

    def test_qa_review_pack_keeps_both_ends_of_correction_not_unrelated_setup(self):
        self.fixture()
        self.record_pair(self.qa_pair())
        reg = get(self.root / "qa/registry.json")
        reg["decisions"][0]["interaction_refs"] = ["QA-001"]
        put(self.root / "qa/registry.json", reg)
        self.record_pair(self.qa_pair(id="QA-002", supersedes="QA-001", change_reason="改口", answer_text="第一個"))
        self.record_pair(self.qa_pair(id="QA-003", kind="setup", question_text="專案放哪裡？", options=[], answer_text="目前工作區"))
        full = self.run_tool("digest").stdout.strip()
        self.run_tool("review-pack", "--id", "REV-QA")
        packet = get(self.root / "qa/review-packs/REV-QA/packet.json")
        self.assertEqual(packet["interview_evidence_ids"], ["QA-001", "QA-002"])
        self.assertEqual([r["id"] for r in packet["review_input"]["registry"]["interactions"]], ["QA-001", "QA-002"])
        self.assertEqual(packet["artifact_digest"], full)
        self.assertEqual(len(get(self.root / "qa/registry.json")["interactions"]), 3)

    def test_qa_review_pack_filters_unselected_questions(self):
        self.fixture()
        reg = get(self.root / "qa/registry.json")
        reg["questions"] = [{"id": qid, "text": "合成問題", "status": "open", "owner": "使用者", "due_or_trigger": "後續",
                              "impact_ids": impacts, "decision_refs": []} for qid, impacts in
                             [("Q-IN", ["REQ-001"]), ("Q-OUT", [])]]
        put(self.root / "qa/registry.json", reg)
        self.record_pair(self.qa_pair(question_id="Q-IN", answer_status="unknown", answer_text="不知道", interpretation="保留缺口"))
        self.record_pair(self.qa_pair(id="QA-002", question_id="Q-OUT"))
        self.run_tool("review-pack", "--id", "REV-SCOPE")
        packet = get(self.root / "qa/review-packs/REV-SCOPE/packet.json")
        self.assertEqual(packet["interview_evidence_ids"], ["QA-001"])

    def test_qa_changes_digest_but_render_and_read_do_not(self):
        before = self.run_tool("digest").stdout.strip()
        self.record_pair(self.qa_pair())
        after = self.run_tool("digest").stdout.strip()
        self.assertNotEqual(before, after)
        self.run_tool("render")
        self.run_tool("show-qa", "--id", "QA-001")
        self.assertEqual(after, self.run_tool("digest").stdout.strip())

    def test_qa_legacy_registry_without_pairs_is_preserved(self):
        reg = get(self.root / "qa/registry.json")
        reg.pop("interactions")
        put(self.root / "qa/registry.json", reg)
        before = (self.root / "qa/registry.json").read_bytes()
        self.run_tool("check")
        self.run_tool("render")
        self.assertEqual((self.root / "qa/registry.json").read_bytes(), before)
        self.assertIn("尚未登錄成對問答", (self.root / "qa/interview.md").read_text(encoding="utf-8"))

    def test_qa_pending_answer_conflicts_with_resolved_question(self):
        self.fixture()
        reg = get(self.root / "qa/registry.json")
        reg["questions"] = [{"id": "Q-001", "text": "匯出模式？", "status": "open", "owner": "使用者", "due_or_trigger": "案例設計前", "decision_refs": []}]
        put(self.root / "qa/registry.json", reg)
        self.record_pair(self.qa_pair(question_id="Q-001", answer_status="pending", answer_text=None, answered_by=None, interpretation=None))
        reg = get(self.root / "qa/registry.json")
        reg["questions"][0].update(status="resolved", decision_refs=["DEC-001"])
        put(self.root / "qa/registry.json", reg)
        self.assertIn("conflicts with resolved question", self.run_tool("check", ok=False).stdout)

    def test_risk_requirement_gaps_warn_in_draft_and_block_scoped_baseline(self):
        reg, _ = self.fixture()
        reg["requirements"][0].pop("risk_assessment")
        put(self.root / "qa/registry.json", reg)
        self.assertIn("risk assessment unassessed", self.run_tool("check").stdout)
        self.refresh_review()
        self.assertIn("risk assessment unassessed", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        self.run_tool("render")
        self.assertIn("未評估", (self.root / "qa/risks.md").read_text(encoding="utf-8"))

    def test_risk_unknown_is_not_low_and_grades_need_project_definitions(self):
        reg, _ = self.fixture()
        self.run_tool("check", "--gate", "baseline")
        self.run_tool("render")
        report = (self.root / "qa/report.html").read_text(encoding="utf-8")
        self.assertIn("待評估／資料不足", report)
        reg["risks"][0]["severity"] = "P1"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("severity is not a defined", self.run_tool("check", ok=False).stdout)

    def test_risk_confirmation_and_stale_requirement_version(self):
        reg, _ = self.fixture()
        assessment = reg["requirements"][0]["risk_assessment"]
        assessment["decision_refs"] = []
        put(self.root / "qa/registry.json", reg)
        self.assertIn("confirmed assessment needs", self.run_tool("check", ok=False).stdout)
        assessment["decision_refs"] = ["DEC-001"]
        reg["requirements"][0]["revision"] = 2
        put(self.root / "qa/registry.json", reg)
        self.assertIn("requirement_revision is missing or stale", self.run_tool("check").stdout)
        self.run_tool("render")
        self.assertIn("評估版本過期", (self.root / "qa/report.html").read_text(encoding="utf-8"))
        self.refresh_review()
        self.assertIn("requirement_revision is missing or stale", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_shared_risk_many_to_many_and_unselected_requirement(self):
        reg, _ = self.fixture()
        other = copy.deepcopy(reg["requirements"][0])
        other.update(id="REQ-002", text="Synthetic second consequence")
        reg["requirements"].append(other)
        unrelated = {"id": "REQ-003", "revision": 1, "text": "Outside this scope", "status": "proposed"}
        reg["requirements"].append(unrelated)
        reg["risks"][0]["requirement_ids"].append("REQ-002")
        extra = {**copy.deepcopy(reg["risks"][0]), "id": "RISK-002", "requirement_ids": ["REQ-001"],
                 "failure": "Synthetic intermittent output", "disposition": "defer", "disposition_reason": "Synthetic scope decision",
                 "residual_risk": "Intermittent behavior remains untested", "decision_refs": ["DEC-001"]}
        reg["risks"].append(extra)
        put(self.root / "qa/registry.json", reg)
        self.refresh_review()
        self.assertIn("REQ-003: risk assessment unassessed", self.run_tool("check", "--gate", "baseline").stdout)
        self.run_tool("render")
        report = ReportParser((self.root / "qa/report.html").read_text(encoding="utf-8"))
        for req_id in ("REQ-001", "REQ-002"):
            self.assertIn('#' + report.records[req_id]['anchor'], report.records['RISK-001']['links'])
            self.assertIn('#' + report.records['RISK-001']['anchor'], report.records[req_id]['links'])
        self.assertIn('#' + report.records['RISK-002']['anchor'], report.records['REQ-001']['links'])
        self.assertTrue(all(link[1:] in report.ids for link in report.links if link.startswith('#')))

    def test_unselected_linked_risk_needs_explicit_disposition(self):
        reg, _ = self.fixture()
        reg["risks"].append({**copy.deepcopy(reg["risks"][0]), "id": "RISK-002", "failure": "Other failure"})
        put(self.root / "qa/registry.json", reg)
        self.refresh_review()
        self.assertIn("unselected risk needs defer", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_no_identified_risk_requires_assessment_reason_and_basis(self):
        reg, case = self.fixture()
        reg["risks"] = []
        reg["scope"]["selected_risk_ids"] = []
        reg["scenarios"][0]["risk_ids"] = []
        case["risk_ids"] = []
        assessment = reg["requirements"][0]["risk_assessment"]
        assessment["rationale"] = "Reviewed isolated cosmetic scope; no additional failure scenario identified"
        put(self.root / "qa/registry.json", reg)
        put(self.root / "qa/cases/TC-001.json", case)
        self.refresh_review()
        self.run_tool("check", "--gate", "baseline")
        self.run_tool("render")
        self.assertIn("本次未辨識風險（不等於零風險）", (self.root / "qa/report.html").read_text(encoding="utf-8"))
        assessment["rationale"] = ""
        put(self.root / "qa/registry.json", reg)
        self.refresh_review()
        self.assertIn("risk assessment missing rationale", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_legacy_risk_render_and_read_do_not_rewrite_history(self):
        reg, _ = self.fixture()
        reg["project"].pop("risk_policy")
        reg["project"].pop("risk_criteria")
        reg["requirements"][0].pop("risk_assessment")
        for key in ("requirement_ids", "severity", "severity_rationale", "likelihood_rationale"):
            reg["risks"][0].pop(key)
        reg["risks"][0]["likelihood"] = "unknown, no field data"
        put(self.root / "qa/registry.json", reg)
        historical = self.root / "qa/baselines/BL-OLD.json"
        historical.write_text('{"synthetic_old_risk_snapshot":true}', encoding="utf-8")
        before = (historical.read_bytes(), (self.root / "qa/registry.json").read_bytes())
        self.assertIn("Legacy risk assessment", self.run_tool("check").stdout)
        self.run_tool("render")
        html = (self.root / "qa/report.html").read_text(encoding="utf-8")
        self.assertIn("未對應需求", html)
        self.assertIn("未評估", html)
        self.assertEqual(before, (historical.read_bytes(), (self.root / "qa/registry.json").read_bytes()))
        self.refresh_review()
        self.assertIn("New baseline requires project.risk_policy", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_risk_invalid_refs_missing_dimensions_and_unconfirmed_criteria(self):
        reg, _ = self.fixture()
        reg["risks"][0]["requirement_ids"] = ["REQ-MISSING"]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("unknown requirements reference", self.run_tool("check", ok=False).stdout)
        reg["risks"][0]["requirement_ids"] = ["REQ-001"]
        reg["risks"][0].pop("severity")
        reg["risks"][0].pop("severity_rationale")
        reg["project"]["risk_criteria"]["status"] = "proposed"
        put(self.root / "qa/registry.json", reg)
        draft = self.run_tool("check").stdout
        self.assertIn("missing severity", draft)
        self.refresh_review()
        result = self.run_tool("check", "--gate", "baseline", ok=False).stdout
        self.assertIn("risk grading criteria not confirmed", result)
        self.assertIn("missing severity_rationale", result)

    def test_risk_change_invalidates_prior_review_and_is_in_review_pack(self):
        reg, _ = self.fixture()
        reg["risks"][0]["severity"] = "low"
        reg["risks"][0]["severity_rationale"] = "Synthetic changed consequence"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("Missing current independent review", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        self.run_tool("review-pack", "--id", "REV-RISK")
        packet = get(self.root / "qa/review-packs/REV-RISK/packet.json")
        self.assertEqual(packet["review_input"]["registry"]["risks"][0]["severity"], "low")
        self.assertIn("risk_criteria", packet["review_input"]["registry"]["project"])

    def test_risk_observation_evidence_survives_review_without_becoming_oracle(self):
        reg, _ = self.fixture()
        path = self.root / "inputs/history.md"
        path.write_text("Synthetic incident observations, not a product promise", encoding="utf-8")
        reg["sources"].append({"id": "SRC-HISTORY", "path": "inputs/history.md", "sha256": sha(path),
                               "locator": "whole file", "kind": "observation", "status": "confirmed"})
        reg["risks"][0]["source_refs"].append("SRC-HISTORY")
        put(self.root / "qa/registry.json", reg)
        self.run_tool("review-pack", "--id", "REV-HISTORY")
        packet = get(self.root / "qa/review-packs/REV-HISTORY/packet.json")
        self.assertIn("SRC-HISTORY", packet["risk_evidence_source_ids"])
        self.assertIn("SRC-HISTORY", [s["id"] for s in packet["review_input"]["registry"]["sources"]])
        self.run_tool("render")
        html = (self.root / "qa/report.html").read_text(encoding="utf-8")
        self.assertIn("風險評估線索；不是產品判準", html)
        report = ReportParser(html)
        self.assertIn('#' + report.records['TC-001']['anchor'], report.records['SRC-HISTORY']['links'])
        reg["acceptance"][0]["source_refs"] = ["SRC-HISTORY"]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("not a confirmed normative source", self.run_tool("check", ok=False).stdout)

    def test_risk_orphan_and_missing_criteria_dimension_block_new_baseline(self):
        reg, _ = self.fixture()
        reg["risks"][0]["requirement_ids"] = []
        reg["project"]["risk_criteria"].pop("severity")
        put(self.root / "qa/registry.json", reg)
        self.assertIn("risk has no direct requirement_ids", self.run_tool("check").stdout)
        self.refresh_review()
        result = self.run_tool("check", "--gate", "baseline", ok=False).stdout
        self.assertIn("risk has no direct requirement_ids", result)
        self.assertIn("missing severity level definitions", result)

    def test_legacy_draft_reads_but_new_baseline_requires_design_migration(self):
        reg, case = self.fixture()
        reg["project"].pop("design_policy")
        reg.pop("coverage_items")
        reg.pop("charters")
        case.pop("coverage_ids")
        case["steps"][0]["checks"][0].pop("coverage_ids")
        put(self.root / "qa/registry.json", reg)
        put(self.root / "qa/cases/TC-001.json", case)
        historical = self.root / "qa/baselines/BL-LEGACY.json"
        historical.write_text('{"synthetic_historical_snapshot":true}', encoding="utf-8")
        before = historical.read_bytes()
        self.assertIn("Legacy design", self.run_tool("check").stdout)
        self.run_tool("render")
        self.assertIn("舊版專案", (self.root / "qa/report.html").read_text(encoding="utf-8"))
        self.refresh_review()
        self.assertIn("New baseline requires", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        self.assertEqual(historical.read_bytes(), before)
        self.run_tool("start-run", "--id", "RUN-LEGACY", "--case", "TC-001", "--sut-version", "fixture1", "--environment", "lab")
        self.run_tool("check-run", "--id", "RUN-LEGACY")

    def test_ac_reference_alone_cannot_satisfy_missing_coverage_item(self):
        reg, _ = self.fixture()
        reg["coverage_items"].append({**reg["coverage_items"][0], "id": "COV-002", "description": "Another selected initial state"})
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")  # An incomplete plan is editable.
        self.refresh_review()
        self.assertIn("COV-002: retained coverage item has no selected case assertion",
                      self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_claimed_item_requires_assertion_and_matching_rule(self):
        reg, case = self.fixture()
        check = case["steps"][0]["checks"][0]
        check["coverage_ids"] = []
        put(self.root / "qa/cases/TC-001.json", case)
        self.assertIn("claimed coverage item lacks an assertion", self.run_tool("check", ok=False).stdout)
        check["coverage_ids"] = ["COV-001"]
        reg["acceptance"].append({**reg["acceptance"][0], "id": "AC-002"})
        reg["coverage_items"][0]["ac_ids"] = ["AC-002"]
        put(self.root / "qa/registry.json", reg)
        put(self.root / "qa/cases/TC-001.json", case)
        self.assertIn("coverage assertion lacks its AC basis", self.run_tool("check", ok=False).stdout)

    def test_empty_or_all_deferred_coverage_cannot_pass_selected_ac(self):
        reg, case = self.fixture()
        case["coverage_ids"] = []
        case["steps"][0]["checks"][0]["coverage_ids"] = []
        put(self.root / "qa/cases/TC-001.json", case)
        for rows in ([], [{**reg["coverage_items"][0], "selection": "defer", "residual_risk": "transition untested", "decision_refs": ["DEC-001"]}]):
            with self.subTest(rows=rows):
                reg["coverage_items"] = rows
                put(self.root / "qa/registry.json", reg)
                self.refresh_review()
                self.assertIn("selected AC has no retained coverage item", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_deferred_item_needs_decision_and_residual_risk(self):
        reg, _ = self.fixture()
        deferred = {**reg["coverage_items"][0], "id": "COV-002", "selection": "defer", "reason": "outside current budget"}
        reg["coverage_items"].append(deferred)
        put(self.root / "qa/registry.json", reg)
        self.assertIn("missing residual_risk", self.run_tool("check", ok=False).stdout)
        deferred["residual_risk"] = "This initial state has no designed check"
        put(self.root / "qa/registry.json", reg)
        self.refresh_review()
        self.assertIn("deferred coverage needs a human decision", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        deferred["decision_refs"] = ["DEC-001"]
        put(self.root / "qa/registry.json", reg)
        self.refresh_review()
        self.run_tool("check", "--gate", "baseline")

    def test_coverage_question_blocks_baseline(self):
        reg, _ = self.fixture()
        reg["questions"] = [{"id": "Q-001", "text": "Input resolution unknown", "status": "open", "owner": "unassigned",
                             "due_or_trigger": "before baseline", "impact_ids": ["COV-001"], "blocks": ["baseline"]}]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("Q-001: unresolved blocker", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_shared_implicit_oracle_requires_once_recorded_human_decision(self):
        reg, case = self.fixture()
        ac = reg["acceptance"][0]
        ac["source_refs"] = []
        ac["oracle"].update(kind="implicit", applies_when="isolated fixture evaluation", limitations="not restart or fault injection")
        ac["decision_refs"] = []
        put(self.root / "qa/registry.json", reg)
        self.assertIn("oracle needs human decision_refs", self.run_tool("check", ok=False).stdout)
        ac["decision_refs"] = ["DEC-001"]
        duplicate = copy.deepcopy(case)
        duplicate["id"] = "TC-002"
        put(self.root / "qa/cases/TC-002.json", duplicate)
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")
        self.assertEqual(len(get(self.root / "qa/registry.json")["decisions"]), 1)

    def test_derived_oracle_needs_relation_and_scoped_comparison_reference(self):
        reg, _ = self.fixture()
        ac = reg["acceptance"][0]
        ac["oracle"].update(kind="derived", applies_when="same synthetic inputs", limitations="reference may share bugs")
        put(self.root / "qa/registry.json", reg)
        self.assertIn("missing relation", self.run_tool("check", ok=False).stdout)
        ac["oracle"]["relation"] = "selected output equals approved prior result for unchanged behavior"
        ac["oracle"]["reference_refs"] = ["SRC-REFERENCE"]
        for sid in ("SRC-REFERENCE", "SRC-OTHER"):
            filename = "inputs/" + sid + ".txt"
            (self.root / filename).write_text("synthetic observation", encoding="utf-8")
            reg["sources"].append({"id": sid, "kind": "observation", "status": "confirmed", "path": filename,
                                   "sha256": sha(self.root / filename), "locator": "whole file"})
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")
        self.run_tool("review-pack", "--id", "REV-DERIVED")
        packet = get(self.root / "qa/review-packs/REV-DERIVED/packet.json")
        source_ids = {s["id"] for s in packet["review_input"]["registry"]["sources"]}
        self.assertIn("SRC-REFERENCE", source_ids)
        self.assertNotIn("SRC-OTHER", source_ids)
        self.assertEqual(packet["comparison_reference_ids"], ["SRC-REFERENCE"])

    def test_experience_source_is_candidate_basis_not_expected(self):
        reg, _ = self.fixture()
        reg["sources"][0]["kind"] = "experience"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("not a confirmed normative source", self.run_tool("check", ok=False).stdout)
        for group in ("requirements", "acceptance"):
            reg[group][0]["source_refs"] = []  # Decision remains the rule basis.
        reg["scenarios"][0].update(origin="experience", source_refs=["SRC-SPEC"])
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")
        self.run_tool("render")
        report = ReportParser((self.root / "qa/report.html").read_text(encoding="utf-8"))
        self.assertIn("候選情境線索；不是產品判準", report.records["TC-001"]["text"])

    def test_exploration_without_oracle_is_plan_not_formal_coverage(self):
        reg, case = self.fixture()
        reg["charters"] = [self.charter()]
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")
        case["coverage_ids"] = []
        case["steps"][0]["checks"][0]["coverage_ids"] = []
        put(self.root / "qa/cases/TC-001.json", case)
        self.refresh_review()
        self.assertIn("retained coverage item has no selected case assertion", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        reg["charters"][0]["findings"] = ["Pretended execution"]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("observations belong in separate session evidence", self.run_tool("check", ok=False).stdout)

    def test_ready_exploration_needs_timebox_and_verified_operations(self):
        reg, _ = self.fixture()
        charter = self.charter()
        charter["timebox_minutes"] = 0
        charter["binding_refs"] = []
        reg["charters"] = [charter]
        put(self.root / "qa/registry.json", reg)
        errors = self.run_tool("check", ok=False).stdout
        self.assertIn("positive integer", errors)
        self.assertIn("missing binding_refs", errors)

    def test_report_coverage_and_exploration_links_do_not_claim_execution(self):
        reg, _ = self.fixture()
        reg["charters"] = [self.charter()]
        reg["coverage_items"][0]["description"] = '<img src=x onerror=alert(1)> boundary item'
        put(self.root / "qa/registry.json", reg)
        original = self.run_tool("digest").stdout
        self.run_tool("render")
        html = (self.root / "qa/report.html").read_text(encoding="utf-8")
        report = ReportParser(html)
        self.assertNotIn("<img ", html)
        for a, b in (("COV-001", "TC-001"), ("COV-001", "AC-001"), ("EXP-001", "SRC-HARNESS")):
            self.assertIn("#" + report.records[b]["anchor"], report.records[a]["links"])
            self.assertIn("#" + report.records[a]["anchor"], report.records[b]["links"])
        self.assertTrue(all(h[1:] in report.ids for h in report.links if h.startswith("#")))
        self.assertEqual(len(report.ids), len(set(report.ids)))
        self.assertIn("不是實際執行覆蓋率", html)
        self.assertIn("探索任務設計（非執行結果）", html)
        self.assertEqual(original, self.run_tool("digest").stdout)
        self.assertIn("| COV | Coverage |", (self.root / "qa/test-design.md").read_text(encoding="utf-8"))

    def test_coverage_change_invalidates_review_and_approval(self):
        reg, _ = self.fixture()
        reg["coverage_items"][0]["description"] += "; refined initial state"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("Missing current independent review", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_unverified_comparison_artifact_is_not_confirmed_oracle(self):
        reg, _ = self.fixture()
        oracle = reg["acceptance"][0]["oracle"]
        oracle.update(kind="derived", relation="same output for unchanged inputs", applies_when="fixture only",
                      limitations="not absolute correctness", reference_refs=["SRC-HARNESS"])
        reg["sources"][1]["status"] = "unconfirmed"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("comparison reference must be a confirmed artifact", self.run_tool("check", ok=False).stdout)

    def test_unknown_coverage_references_are_rejected(self):
        _, case = self.fixture()
        case["coverage_ids"] = ["COV-MISSING"]
        case["steps"][0]["checks"][0]["coverage_ids"] = ["COV-MISSING"]
        put(self.root / "qa/cases/TC-001.json", case)
        self.assertIn("unknown coverage_items reference", self.run_tool("check", ok=False).stdout)

    def test_teaching_fixture_runs_boundary_cases_and_preserves_old_evidence(self):
        demo = TOOL.with_name("demo_counter.py")
        for count, expected in ((48, False), (49, False), (50, True), (51, True)):
            with self.subTest(count=count):
                record = self.root / ("demo-" + str(count) + ".json")
                args = [sys.executable, str(demo), "--count", str(count), "--record", str(record)]
                result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                observed = get(record)
                self.assertIs(observed["alarm"], expected)
                self.assertEqual(observed["count"], count)
                self.assertTrue(observed["demo"])
                before = record.read_bytes()
                again = subprocess.run(args, capture_output=True)
                self.assertNotEqual(again.returncode, 0)
                self.assertEqual(record.read_bytes(), before)

    def test_init_idempotent_and_no_remote(self):
        session = self.root / "qa/session.md"
        session.write_text("Keep my decisions", encoding="utf-8")
        self.run_tool("init")
        self.assertEqual(session.read_text(encoding="utf-8"), "Keep my decisions")
        self.assertEqual(self.git("remote"), "")
        self.run_tool("check")
        self.run_tool("check", "--gate", "baseline", ok=False)

    def test_proposed_requirement_allows_null_confirmation(self):
        reg = get(self.root / "qa/registry.json")
        reg["requirements"] = [{"id": "REQ-001", "text": "Draft, not yet confirmed", "revision": 1,
                                "status": "proposed", "source_refs": [], "decision_refs": [], "confirmation": None}]
        put(self.root / "qa/registry.json", reg)
        self.run_tool("check")
        self.run_tool("digest")

    def test_render_explains_ids_without_changing_records(self):
        self.fixture()
        design_digest = self.run_tool("digest").stdout
        before = {p: p.read_bytes() for p in (self.root / "qa/registry.json", self.root / "qa/cases/TC-001.json")}
        self.run_tool("render")
        spec = (self.root / "qa/spec.md").read_text(encoding="utf-8")
        cases = (self.root / "qa/test-cases.md").read_text(encoding="utf-8")
        trace = (self.root / "qa/traceability.md").read_text(encoding="utf-8")
        self.assertIn("| REQ | Requirement | 需求 |", spec)
        self.assertIn("| TC | Test Case | 測試案例 |", cases)
        self.assertIn("| AC | Acceptance Criterion | 驗收條件 |", trace)
        for content in (spec, cases, trace):
            self.assertIn("不代表優先度、版本、確認狀態或測試結果", content)
        self.assertLess(spec.index("## 編號說明"), spec.index("REQ-001"))
        self.assertTrue((self.root / "qa/id-glossary.md").is_file())
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertEqual(design_digest, self.run_tool("digest").stdout)
        self.assertTrue((self.root / "qa/report.html").is_file())

    def test_html_bidirectional_and_transitive_sources(self):
        reg, case = self.fixture()
        # The case's AC has no direct source; its parent requirement supplies it.
        reg['acceptance'][0]['source_refs'] = []
        (self.root / 'inputs/unused.md').write_text('Not used by any case')
        reg['sources'].append({'id': 'SRC-UNUSED', 'path': 'inputs/unused.md',
                               'sha256': sha(self.root / 'inputs/unused.md'), 'kind': 'observation',
                               'status': 'unconfirmed', 'locator': 'whole file'})
        put(self.root / 'qa/registry.json', reg)
        self.run_tool('render')
        report = ReportParser((self.root / 'qa/report.html').read_text(encoding="utf-8"))
        tc = report.records['TC-001']
        for sid in ('SRC-SPEC', 'SRC-HARNESS'):
            src = report.records[sid]
            self.assertIn('#' + src['anchor'], tc['links'])
            self.assertIn('#' + tc['anchor'], src['links'])
        self.assertNotIn('#' + report.records['SRC-UNUSED']['anchor'], tc['links'])
        self.assertIn('目前沒有案例引用', report.records['SRC-UNUSED']['text'])
        self.assertIn('#' + report.records['REQ-001']['anchor'], tc['links'])
        self.assertIn('預期結果依據：步驟 1', tc['text'])
        self.assertIn('操作／觀測依據', tc['text'])
        for field in ('reset fixture to OFF', 'evaluate once', 'on return', 'output ON', 'close fixture'):
            self.assertIn(field, tc['text'])
        self.assertEqual(len(report.ids), len(set(report.ids)))
        self.assertTrue(all(href[1:] in report.ids for href in report.links if href.startswith('#')))

    def test_html_missing_changed_and_unconfirmed_references(self):
        reg, case = self.fixture()
        reg['acceptance'][0]['source_refs'].append('SRC-MISSING')
        reg['requirements'][0]['status'] = 'proposed'
        reg['sources'][0]['status'] = 'unconfirmed'
        (self.root / 'inputs/spec.md').write_text('A different revision')
        (self.root / 'inputs/harness.md').unlink()
        case['ac_ids'].append('AC-MISSING')
        put(self.root / 'qa/registry.json', reg)
        put(self.root / 'qa/cases/TC-001.json', case)
        self.run_tool('render')
        report = ReportParser((self.root / 'qa/report.html').read_text(encoding="utf-8"))
        self.assertIn('來源已變更', report.records['SRC-SPEC']['text'])
        self.assertIn('unconfirmed', report.records['SRC-SPEC']['text'])
        self.assertIn('來源檔案不可用', report.records['SRC-HARNESS']['text'])
        self.assertIn('SRC-MISSING（未登錄）', report.records['TC-001']['text'])
        self.assertIn('AC-MISSING（未登錄）', report.records['TC-001']['text'])
        self.assertIn('proposed', report.records['REQ-001']['text'])
        self.assertTrue(all(href[1:] in report.ids for href in report.links if href.startswith('#')))

    def test_html_escapes_content_and_restricts_file_links(self):
        reg, case = self.fixture()
        hostile = '<script>alert("test")</script><img src=x onerror=alert(1)>'
        reg['project']['name'] = hostile
        reg['sources'][0]['excerpt'] = hostile
        reg['sources'][1]['path'] = '../outside.md'
        case['title'] = hostile
        # Exercise URL-reserved characters with a filename valid on Windows too.
        filenames = [('inputs/規格 #1% &.md',
                      '../inputs/%E8%A6%8F%E6%A0%BC%20%231%25%20%26.md')]
        if os.name != 'nt':
            # '?' is a legal POSIX filename character but reserved on Windows.
            filenames.append(('inputs/規格 #1?.md',
                              '../inputs/%E8%A6%8F%E6%A0%BC%20%231%3F.md'))
        for filename, expected_href in filenames:
            with self.subTest(filename=filename):
                (self.root / filename).write_text('Text', encoding='utf-8')
                reg['sources'][0]['path'] = filename
                put(self.root / 'qa/registry.json', reg)
                put(self.root / 'qa/cases/TC-001.json', case)
                self.run_tool('render')
                html = (self.root / 'qa/report.html').read_text(encoding='utf-8')
                report = ReportParser(html)
                self.assertNotIn('<script>', html)
                self.assertNotIn('<img ', html)
                self.assertEqual(report.scripts, [])
                self.assertIn(hostile, report.records['TC-001']['text'])
                # Filename characters must not become URL fragments or queries.
                hrefs = [x for x in report.links if unquote(x) == '../' + filename]
                self.assertTrue(hrefs, filename)
                for href in hrefs:
                    self.assertEqual(href, expected_href)
                    parsed = urlsplit(href)
                    self.assertEqual((parsed.query, parsed.fragment), ('', ''))
                    self.assertTrue((self.root / 'qa' / unquote(parsed.path)).is_file())
                self.assertNotIn('../../outside.md', report.links)
                self.assertIn('路徑不安全', report.records['SRC-HARNESS']['text'])
                self.assertTrue(all(not x.startswith(('https:', 'http:', 'javascript:', 'file:')) for x in report.links))

    def test_html_empty_project_and_custom_glossary(self):
        html = (self.root / 'qa/report.html').read_text(encoding="utf-8")
        self.assertIn('尚未登錄來源', html)
        self.assertIn('尚未建立測試案例', html)
        reg = get(self.root / 'qa/registry.json')
        reg['project']['id_glossary'] = {'SRC': {'english': None},
                                       'BIZ': {'english': 'Business Rule', 'meaning': '業務規則', 'purpose': '追蹤規則'}}
        put(self.root / 'qa/registry.json', reg)
        self.run_tool('render')
        html = (self.root / 'qa/report.html').read_text(encoding="utf-8")
        self.assertIn('SRC＝待確認', html)
        self.assertIn('Business Rule', html)

    def test_render_uses_project_definitions_and_marks_unknown_ids(self):
        reg, _ = self.fixture()
        reg["requirements"] += [{**reg["requirements"][0], "id": rid} for rid in ("BIZ-007", "LEGACY-09")]
        reg["project"]["id_glossary"] = {
            "BIZ": {"english": "Business Rule", "meaning": "業務規則", "purpose": "追蹤業務規則", "basis": "synthetic fixture"},
            "REQ": {"english": None, "meaning": None, "purpose": None},
        }
        put(self.root / "qa/registry.json", reg)
        self.run_tool("render")
        spec = (self.root / "qa/spec.md").read_text(encoding="utf-8")
        self.assertIn("| BIZ | Business Rule | 業務規則 |", spec)
        self.assertIn("| LEGACY | 待確認 | 待確認 |", spec)
        self.assertIn("| REQ | 待確認 | 待確認 |", spec)
        self.assertNotIn("| REQ | Requirement |", spec)
        self.assertIn("LEGACY-09", spec)
        self.assertNotIn("LEGACY-009", spec)

    def test_inventory_change_and_private_exclusions(self):
        (self.root / "inputs").mkdir()
        (self.root / "inputs/a.md").write_text("one")
        (self.root / ".env").write_text("SECRET=not-for-history")
        self.run_tool("inventory")
        (self.root / "inputs/a.md").write_text("two")
        report = json.loads(self.run_tool("inventory").stdout)
        self.assertEqual(report["changed"], ["inputs/a.md"])
        self.run_tool("checkpoint", "-m", "initial", "--include", "inputs")
        self.assertNotIn(".env", self.git("ls-files"))
        self.assertIn("inputs/a.md", self.git("ls-files"))

    def test_checkpoint_preserves_staged_work(self):
        (self.root / "mine.txt").write_text("user staging")
        self.git("add", "mine.txt")
        before = self.git("diff", "--cached")
        self.run_tool("checkpoint", "-m", "must not mix", ok=False)
        self.assertEqual(self.git("diff", "--cached"), before)

    def test_parent_repository_needs_explicit_standalone(self):
        child = self.root / "child"
        child.mkdir()
        self.run_tool("init", root=child, ok=False)
        self.assertFalse((child / "qa").exists())
        self.run_tool("init", "--standalone", root=child)
        self.assertTrue((child / ".git").exists())

    def test_baseline_success_immutable_and_tag(self):
        self.fixture()
        self.run_tool("check", "--gate", "baseline")
        self.run_tool("baseline", "--id", "BL-001", "--approval", "qa/approvals/APP-001.json")
        previous = (self.root / "qa/baselines/BL-001.json").read_bytes()
        self.run_tool("baseline", "--id", "BL-001", "--approval", "qa/approvals/APP-001.json", ok=False)
        self.assertEqual((self.root / "qa/baselines/BL-001.json").read_bytes(), previous)
        self.run_tool("checkpoint", "-m", "baseline", "--tag", "qa-baseline-BL-001")
        self.assertIn("inputs/spec.md", self.git("ls-files"))
        self.assertEqual(self.git("tag").strip(), "qa-baseline-BL-001")
        self.run_tool("checkpoint", "-m", "duplicate tag", "--tag", "qa-baseline-BL-001", ok=False)

    def test_unconfirmed_expected_and_claimed_coverage_rejected(self):
        reg, case = self.fixture()
        reg["acceptance"][0]["status"] = "proposed"
        put(self.root / "qa/registry.json", reg)
        self.assertIn("unconfirmed", self.run_tool("check", ok=False).stdout)
        reg["acceptance"][0]["status"] = "confirmed"
        put(self.root / "qa/registry.json", reg)
        case["steps"][0]["checks"] = []
        put(self.root / "qa/cases/TC-001.json", case)
        self.assertIn("no product assertion", self.run_tool("check", ok=False).stdout)

    def test_stale_sources_decisions_and_review_rejected(self):
        self.fixture()
        source = self.root / "inputs/spec.md"
        original = source.read_bytes()
        source.write_text("Changed normative rule")
        self.assertIn("Sources changed", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        source.write_bytes(original)
        (self.root / "qa/decisions/DEC-001.md").write_text("Changed synthetic approval")
        self.assertIn("Missing current", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_same_session_and_unselected_scope_gap(self):
        reg, _ = self.fixture()
        path = self.root / "qa/reviews/REV-001.json"
        review = get(path)
        review["independence"] = "same-session"
        put(path, review)
        self.assertIn("Missing current", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        reg["scope"]["selected_case_ids"] = []
        put(self.root / "qa/registry.json", reg)
        self.assertIn("no retained case", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_requirement_level_question_blocks_selected_cases(self):
        reg, _ = self.fixture()
        reg["questions"] = [{"id": "Q-001", "text": "Conflicting requirement authority", "status": "open", "owner": "unassigned",
                             "due_or_trigger": "before baseline", "impact_ids": ["REQ-001"], "blocks": ["baseline"], "decision_refs": []}]
        put(self.root / "qa/registry.json", reg)
        self.assertIn("Q-001: unresolved blocker", self.run_tool("check", "--gate", "baseline", ok=False).stdout)

    def test_stale_approval_does_not_create_baseline(self):
        self.fixture()
        path = self.root / "qa/approvals/APP-001.json"
        approval = get(path)
        approval["artifact_digest"] = "previous-content"
        put(path, approval)
        result = self.run_tool("baseline", "--id", "BL-001", "--approval", "qa/approvals/APP-001.json", ok=False)
        self.assertIn("stale", result.stderr)
        self.assertFalse((self.root / "qa/baselines/BL-001.json").exists())

    def test_review_packet_and_render_dont_claim_execution(self):
        self.fixture()
        self.run_tool("review-pack", "--id", "REV-001")
        self.run_tool("review-pack", "--id", "REV-001", ok=False)
        self.run_tool("render")
        self.assertIn("不是執行報告", (self.root / "qa/test-cases.md").read_text(encoding="utf-8"))

    def test_review_handoff_preserves_design_and_question_budget(self):
        self.fixture()
        session = self.root / "qa/session.md"
        session.write_text("Synthetic session: default budget 10; asked 5; active.\n", encoding="utf-8")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*")
                  if p.is_file() and ".git" not in p.relative_to(self.root).parts}
        original_digest = self.run_tool("digest").stdout.strip()
        self.run_tool("review-pack", "--id", "REV-HANDOFF")
        packet = get(self.root / "qa/review-packs/REV-HANDOFF/packet.json")
        self.assertEqual(packet["handoff"]["protocol_version"], 1)
        self.assertEqual(packet["handoff"]["target_skill"], "genai-test-review")
        self.assertEqual(packet["artifact_digest"], original_digest)
        self.assertEqual(self.run_tool("digest").stdout.strip(), original_digest)
        self.assertEqual(packet["review_input"]["cases"]["TC-001"], get(self.root / "qa/cases/TC-001.json"))
        for relative, content in before.items():
            self.assertEqual((self.root / relative).read_bytes(), content, str(relative))

    def test_returned_review_cannot_approve_findings_or_follow_changed_design(self):
        _, case = self.fixture()
        self.run_tool("review-pack", "--id", "REV-HANDOFF")
        packet = get(self.root / "qa/review-packs/REV-HANDOFF/packet.json")
        # Synthetic returned review, not a real independent or product review.
        returned = {"id": "REV-RETURNED", "artifact_digest": packet["artifact_digest"],
                    "reviewer": "synthetic-reviewer", "session": "synthetic-fresh-session",
                    "at": "2026-11-12T00:00:00Z", "independence": "fresh-session",
                    "rounds": ["traceability", "executable", "coverage", "consistency"],
                    "findings": [{"id": "F-001", "round": "executable", "case_ids": ["TC-001"],
                                  "rule_refs": ["AC-001"], "issue": "Synthetic observation gap",
                                  "evidence": "Synthetic fixture step 1", "proposal": "Design owner to resolve",
                                  "status": "open", "disposition": None}]}
        path = self.root / "qa/reviews/REV-RETURNED.json"
        put(path, returned)
        self.assertEqual(self.run_tool("digest").stdout.strip(), packet["artifact_digest"])
        self.assertIn("F-001: unresolved finding", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        case["title"] = "Revised synthetic design"
        put(self.root / "qa/cases/TC-001.json", case)
        self.assertNotEqual(self.run_tool("digest").stdout.strip(), packet["artifact_digest"])
        self.assertIn("Missing current independent review rounds", self.run_tool("check", "--gate", "baseline", ok=False).stdout)
        self.assertEqual(get(path), returned)
        self.assertEqual(get(self.root / "qa/review-packs/REV-HANDOFF/packet.json"), packet)

    def test_run_no_fake_pass_or_changed_evidence(self):
        self.fixture()
        self.run_tool("start-run", "--id", "RUN-001", "--case", "TC-001", "--sut-version", "build1", "--environment", "lab1")
        path = self.root / "qa/runs/RUN-001.json"
        run = get(path)
        self.assertEqual(run["status"], "NOT_RUN")
        self.run_tool("check-run", "--id", "RUN-001")
        run["status"] = "PASS"
        put(path, run)
        self.run_tool("check-run", "--id", "RUN-001", ok=False)
        evidence = self.root / "qa/evidence/run1.log"
        evidence.write_text("Synthetic fixture output ON")
        run.update({"started_at": "2026-11-09T00:00:00Z", "finished_at": "2026-11-09T00:00:01Z", "operator": "synthetic-runner"})
        run["steps"][0].update({"status": "PASS", "actual": "ON", "at": "2026-11-09T00:00:01Z",
                                "evidence": [{"path": "qa/evidence/run1.log", "sha256": sha(evidence)}]})
        put(path, run)
        self.run_tool("check-run", "--id", "RUN-001")
        evidence.write_text("altered")
        self.assertIn("hash mismatch", self.run_tool("check-run", "--id", "RUN-001", ok=False).stdout)
        run["case_snapshot"]["title"] = "changed"
        put(path, run)
        self.assertIn("snapshot changed", self.run_tool("check-run", "--id", "RUN-001", ok=False).stdout)

    def test_path_escape_and_symlink_rejected(self):
        self.fixture()
        self.run_tool("baseline", "--id", "../oops", "--approval", "qa/approvals/APP-001.json", ok=False)
        try:
            (self.root / "outside").symlink_to(self.temp.name, target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable")
        self.run_tool("checkpoint", "-m", "reject symlink", "--include", "outside", ok=False)
        self.assertEqual(self.git("diff", "--cached"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
