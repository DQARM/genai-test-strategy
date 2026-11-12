#!/usr/bin/env python3
"""Local QA records and version checkpoints. Python 3.10+, stdlib + Git only."""
import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import quote

VERSION = "1.4.0"
DESIGN_POLICY = "coverage-items-v1"
TECHNIQUES = {"equivalence", "boundary-2", "boundary-3", "decision-table",
              "state-transition", "pairwise", "scenario", "experience"}
ID_TERMS = {
    "SRC": ("Source", "資料來源", "追蹤文件、操作指南或其他依據"),
    "REQ": ("Requirement", "需求", "追蹤單一產品需求"),
    "AC": ("Acceptance Criterion", "驗收條件", "定義可觀測且可判定的產品條件"),
    "Q": ("Question", "待釐清問題", "追蹤未決事項、責任人與確認時點"),
    "DEC": ("Decision", "決策", "記錄人的決定與依據"),
    "RISK": ("Risk", "風險", "追蹤失敗情境、影響與取捨"),
    "SC": ("Scenario", "測試情境", "表示待選或已選的測試情境"),
    "COV": ("Coverage", "覆蓋項目", "表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage"),
    "EXP": ("Exploration", "探索任務", "限定探索目的、時間與觀察；EXP 取自 Exploration"),
    "TC": ("Test Case", "測試案例", "保存完整前置、步驟、判準與證據要求"),
    "REV": ("Review", "審查紀錄", "記錄特定版本的案例審查"),
    "F": ("Finding", "審查發現", "追蹤具體問題與處置"),
    "APP": ("Approval", "核可紀錄", "記錄人對明確內容與範圍的核可"),
    "BL": ("Baseline", "案例基線", "凍結已核可的案例版本"),
    "RUN": ("Run", "測試執行紀錄", "保存某次實際執行的觀察與證據"),
}
ROUNDS = ["traceability", "executable", "coverage", "consistency"]
GROUPS = ["sources", "decisions", "questions", "requirements", "acceptance", "risks", "scenarios"]
OPTIONAL_GROUPS = ["coverage_items", "charters"]
GROUPS += OPTIONAL_GROUPS
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
PRIVATE = re.compile(r"(^\.env($|\.)|\.(pem|key|p12|pfx)$|^id_(rsa|ed25519)$|^credentials($|\.))", re.I)
PLACEHOLDERS = {"", "tbd", "todo", "unknown", "待確認", "待填", "待補", "未確認", "..."}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fail(message):
    raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if exclusive:
        with path.open("x", encoding="utf-8") as out:
            out.write(content)
    else:
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)


def safe(root, rel):
    p = Path(rel)
    if str(rel) == ".":
        return root
    if p.is_absolute() or ".." in p.parts or ".git" in p.parts or not p.parts:
        fail(f"Use a project-relative path without traversal: {rel}")
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            fail(f"Symlinks are not followed: {rel}")
    if not current.resolve().is_relative_to(root):
        fail(f"Path escapes project: {rel}")
    return current


def git(root, *args, check=True):
    env = os.environ.copy()
    # Do not accidentally operate on a repository selected by inherited Git variables.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env["GIT_LITERAL_PATHSPECS"] = "1"
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, env=env)
    if check and p.returncode:
        fail(p.stderr.decode("utf-8", "replace").strip() or "Git operation failed")
    return p


def repo(root):
    if not shutil.which("git"):
        fail("Git is required. Install Git locally; no Git server is needed.")
    p = git(root, "rev-parse", "--show-toplevel", check=False)
    if p.returncode or Path(os.fsdecode(p.stdout).strip()).resolve() != root:
        fail("Project root must be the exact Git worktree root; run init first.")


def meaningful(value):
    if isinstance(value, str):
        return value.strip().lower() not in PLACEHOLDERS
    return value is not None and value != [] and value != {}


def load(root):
    marker = safe(root, ".qa-project.json")
    if not marker.is_file():
        fail("Not initialized: run init for this project root.")
    if read(marker).get("schema_version") != 1:
        fail("Unsupported project schema.")
    reg = read(safe(root, "qa/registry.json"))
    cases = {}
    for p in sorted(safe(root, "qa/cases").glob("*.json")):
        safe(root, p.relative_to(root))
        case = read(p)
        if case.get("id") != p.stem or p.stem in cases:
            fail(f"Case ID must equal unique filename: {p.name}")
        cases[p.stem] = case
    return reg, cases


def artifacts(root):
    reg, cases = load(root)
    basis = {}
    records = reg.get("decisions", []) + [r.get("confirmation") or {} for group in ("requirements", "acceptance") for r in reg.get(group, [])]
    for item in records:
        reference = item.get("evidence_ref")
        if reference:
            rel = reference.split("#")[0]
            path = safe(root, rel)
            basis[rel] = file_hash(path) if path.is_file() else None
    return {"registry": reg, "cases": cases,
            "decision_evidence_hashes": basis,
            "strategy": safe(root, "qa/strategy.md").read_text(encoding="utf-8"),
            "plan": safe(root, "qa/plan.md").read_text(encoding="utf-8")}


def snapshot_digest(root):
    return digest(artifacts(root))


def approval_ok(root, item):
    if not isinstance(item, dict):
        return False
    if not all(meaningful(item.get(k)) for k in ("by", "at", "evidence_ref")):
        return False
    return safe(root, str(item["evidence_ref"]).split("#")[0]).is_file()


def inspect(root, gate="draft"):
    reg, cases = load(root)
    errors, warnings = [], []
    def error(msg):
        errors.append(msg)
    def require(obj, keys, label):
        if not isinstance(obj, dict):
            error(f"{label}: expected an object")
            return
        for key in keys:
            if not meaningful(obj.get(key)):
                error(f"{label}: missing {key}")
    maps = {}
    all_ids = set()
    for group in GROUPS:
        rows = reg.get(group, [] if group in OPTIONAL_GROUPS else None)
        if not isinstance(rows, list):
            error(f"registry.{group} must be a list")
            rows = []
        maps[group] = {}
        for row in rows:
            rid = row.get("id", "")
            if not re.fullmatch(r"[A-Z][A-Z0-9]*-[A-Za-z0-9_-]+", rid) or rid in all_ids:
                error(f"Invalid or duplicate record ID: {rid}")
            all_ids.add(rid)
            maps[group][rid] = row
    def refs(ids, group, label):
        if not isinstance(ids, list):
            error(f"{label}: references must be a list")
            return []
        out = []
        for rid in ids:
            if rid not in maps[group]:
                error(f"{label}: unknown {group} reference {rid}")
            else:
                out.append(maps[group][rid])
        return out
    stale = set()
    for sid, source in maps["sources"].items():
        require(source, ["path", "sha256", "locator", "kind", "status"], sid)
        if source.get("kind") not in ("normative", "harness", "observation", "experience"):
            error(f"{sid}: invalid source kind")
        try:
            path = safe(root, source.get("path", ""))
            if not path.is_file() or file_hash(path) != source.get("sha256"):
                stale.add(sid)
        except ValueError as exc:
            error(str(exc))
        if sid in stale:
            warnings.append(f"{sid}: source missing or changed; re-read and assess impact")
    for did, decision in maps["decisions"].items():
        require(decision, ["statement"], did)
        if not approval_ok(root, decision):
            error(f"{did}: needs real decision maker, time and local evidence_ref")
    for group in ("requirements", "acceptance"):
        for rid, rule in maps[group].items():
            require(rule, ["text", "revision", "status"], rid)
            if rule.get("status") not in ("proposed", "confirmed", "superseded"):
                error(f"{rid}: invalid rule status")
            sr = refs(rule.get("source_refs", []), "sources", rid)
            dr = refs(rule.get("decision_refs", []), "decisions", rid)
            if rule.get("status") == "confirmed":
                if not approval_ok(root, rule.get("confirmation")):
                    error(f"{rid}: confirmed requires human confirmation evidence")
                if not sr and not dr:
                    error(f"{rid}: confirmed rule has no basis")
                for source in sr:
                    if source.get("kind") != "normative" or source.get("status") != "confirmed":
                        error(f"{rid}: {source['id']} is not a confirmed normative source")
            if group == "acceptance":
                parents = refs(rule.get("requirement_ids", []), "requirements", rid)
                oracle = rule.get("oracle") or {}
                kind = oracle.get("kind", "specified")
                if kind not in ("specified", "derived", "implicit"):
                    error(f"{rid}: invalid oracle kind")
                comparison_refs = refs(oracle.get("reference_refs", []), "sources", rid + ".oracle")
                if rule.get("status") == "confirmed":
                    if not parents or any(p.get("status") != "confirmed" for p in parents):
                        error(f"{rid}: confirmed AC needs confirmed parent requirement")
                    require(rule, ["oracle"], rid)
                    require(rule.get("oracle", {}), ["observe", "when", "tolerance"], rid)
                    if kind in ("derived", "implicit"):
                        require(oracle, ["applies_when", "limitations"], rid + ".oracle")
                        if not dr:
                            error(f"{rid}: derived/implicit oracle needs human decision_refs")
                    if kind == "derived":
                        require(oracle, ["relation"], rid + ".oracle")
                        for source in comparison_refs:
                            if source.get("status") != "confirmed" or source.get("kind") == "experience":
                                error(f"{rid}: comparison reference must be a confirmed artifact, not an experience checklist")
    for qid, question in maps["questions"].items():
        require(question, ["text", "status", "owner", "due_or_trigger"], qid)
        if question.get("status") not in ("open", "resolved", "deferred"):
            error(f"{qid}: invalid question status")
        if question.get("status") == "resolved":
            if not question.get("decision_refs"):
                error(f"{qid}: resolved question needs decision_refs")
            refs(question.get("decision_refs", []), "decisions", qid)
    for rid, risk in maps["risks"].items():
        require(risk, ["failure", "impact", "likelihood", "uncertainty", "priority", "rationale"], rid)
    for sid, scenario in maps["scenarios"].items():
        require(scenario, ["description", "category", "selection", "reason"], sid)
        refs(scenario.get("ac_ids", []), "acceptance", sid)
        refs(scenario.get("risk_ids", []), "risks", sid)
        refs(scenario.get("source_refs", []), "sources", sid)
        if scenario.get("origin", "specification") not in ("specification", "experience", "mixed"):
            error(f"{sid}: invalid scenario origin")
        if scenario.get("selection") not in ("keep", "merge", "defer", "clarify"):
            error(f"{sid}: invalid selection")
        if scenario.get("selection") == "merge":
            targets = refs([scenario.get("merged_into")], "scenarios", sid)
            if not targets or targets[0].get("selection") != "keep":
                error(f"{sid}: merged_into must target a retained scenario")
    scope = reg.get("scope", {})
    policy = reg.get("project", {}).get("design_policy")
    if policy not in (None, DESIGN_POLICY):
        error("Unsupported project.design_policy")
    if policy is None:
        warnings.append("Legacy design: coverage items not adopted; draft editing/render remain available.")
    for cov_id, cov in maps["coverage_items"].items():
        require(cov, ["ac_ids", "technique", "description", "selection", "reason"], cov_id)
        refs(cov.get("ac_ids", []), "acceptance", cov_id)
        refs(cov.get("risk_ids", []), "risks", cov_id)
        refs(cov.get("scenario_ids", []), "scenarios", cov_id)
        refs(cov.get("decision_refs", []), "decisions", cov_id)
        if cov.get("technique") not in TECHNIQUES:
            error(f"{cov_id}: invalid test design technique")
        if cov.get("selection") not in ("keep", "defer"):
            error(f"{cov_id}: invalid coverage selection")
        if cov.get("selection") == "defer":
            require(cov, ["residual_risk"], cov_id)
    for exp_id, charter in maps["charters"].items():
        require(charter, ["title", "status"], exp_id)
        if charter.get("status") not in ("draft", "ready", "retired"):
            error(f"{exp_id}: invalid charter status")
        acs = refs(charter.get("ac_ids", []), "acceptance", exp_id)
        refs(charter.get("source_refs", []), "sources", exp_id)
        refs(charter.get("question_ids", []), "questions", exp_id)
        bindings = refs(charter.get("binding_refs", []), "sources", exp_id)
        if any(k in charter for k in ("actual", "result", "findings")):
            error(f"{exp_id}: exploration observations belong in separate session evidence")
        if charter.get("status") == "ready":
            require(charter, ["mission", "scope", "timebox_minutes", "preconditions", "actions",
                              "stop_conditions", "cleanup", "binding_refs"], exp_id)
            minutes = charter.get("timebox_minutes")
            if type(minutes) is not int or minutes <= 0:
                error(f"{exp_id}: timebox_minutes must be a positive integer")
            for ac in acs:
                if ac.get("status") != "confirmed":
                    error(f"{exp_id}: judging an exploration requires confirmed AC")
            for binding in bindings:
                if binding.get("kind") not in ("normative", "harness") or binding.get("status") != "confirmed":
                    error(f"{exp_id}: exploration operations need confirmed bindings")
            for step in charter.get("actions", []):
                require(step, ["action", "observe", "evidence"], exp_id + ".actions")
            for key in ("preconditions", "cleanup"):
                for step in charter.get(key, []):
                    require(step, ["action", "verify"], exp_id + "." + key)
    selected = scope.get("selected_case_ids", [])
    for key, group in (("selected_ac_ids", "acceptance"), ("selected_risk_ids", "risks"),
                       ("selected_scenario_ids", "scenarios")):
        refs(scope.get(key, []), group, "scope")
    for cid in selected:
        if cid not in cases:
            error(f"scope: unknown case {cid}")
    for cid, case in cases.items():
        require(case, ["title", "revision", "status"], cid)
        status = case.get("status")
        if status not in ("draft", "blocked", "ready", "retired"):
            error(f"{cid}: invalid case status")
        acs = refs(case.get("ac_ids", []), "acceptance", cid)
        refs(case.get("risk_ids", []), "risks", cid)
        refs(case.get("scenario_ids", []), "scenarios", cid)
        refs(case.get("blockers", []), "questions", cid)
        claimed_cov = refs(case.get("coverage_ids", []), "coverage_items", cid)
        for cov in claimed_cov:
            if not set(cov.get("ac_ids", [])) <= set(case.get("ac_ids", [])):
                error(f"{cid}: coverage item AC must be linked by the case")
        if "actual" in case or "result" in case:
            error(f"{cid}: Actual/result belongs in runs, not case design")
        complete = status == "ready" or (gate == "baseline" and cid in selected)
        if not complete:
            warnings.append(f"{cid}: {status}; not a ready executable case")
            continue
        if status != "ready":
            error(f"{cid}: selected case is not ready")
        if case.get("blockers"):
            error(f"{cid}: ready case has blockers")
        require(case, ["purpose", "level", "type", "environment", "preconditions", "data",
                      "steps", "cleanup", "independence", "verdict_rules", "ac_ids"], cid)
        if case.get("type") not in ("manual", "automated"):
            error(f"{cid}: type must be manual or automated")
        if case.get("level") not in ("unit", "integration", "system", "acceptance"):
            error(f"{cid}: invalid test level")
        if any(a.get("status") != "confirmed" for a in acs):
            error(f"{cid}: Expected cannot depend on unconfirmed AC")
        env = case.get("environment", {})
        require(env, ["target", "build_binding", "tools", "binding_refs"], cid + ".environment")
        bindings = refs(env.get("binding_refs", []), "sources", cid + ".environment")
        for source in bindings:
            if source.get("kind") not in ("harness", "normative") or source.get("status") != "confirmed":
                error(f"{cid}: operation binding must be confirmed harness or normative source")
        for key in ("preconditions", "cleanup"):
            for i, step in enumerate(case.get(key, []), 1):
                require(step, ["action", "verify"], f"{cid}.{key}[{i}]")
        assertions = 0
        asserted_ac = set()
        asserted_cov = set()
        for i, step in enumerate(case.get("steps", []), 1):
            label = f"{cid}.step[{i}]"
            if step.get("n") != i:
                error(f"{label}: numbering must be consecutive from 1")
            require(step, ["action", "input", "observe", "when", "evidence"], label)
            for assertion in step.get("checks", []):
                assertions += 1
                require(assertion, ["expected", "rule_refs"], label)
                ar = refs(assertion.get("rule_refs", []), "acceptance", label)
                asserted_ac.update(assertion.get("rule_refs", []))
                for ac in ar:
                    if ac.get("status") != "confirmed" or ac["id"] not in case.get("ac_ids", []):
                        error(f"{label}: assertion must cite a confirmed linked AC")
                for cov in refs(assertion.get("coverage_ids", []), "coverage_items", label):
                    if cov["id"] not in case.get("coverage_ids", []):
                        error(f"{label}: assertion coverage item must be linked by the case")
                    if not set(cov.get("ac_ids", [])) <= set(assertion.get("rule_refs", [])):
                        error(f"{label}: coverage assertion lacks its AC basis")
                    asserted_cov.add(cov["id"])
        if not assertions:
            error(f"{cid}: no product assertion with rule basis")
        if set(case.get("ac_ids", [])) - asserted_ac:
            error(f"{cid}: claimed AC coverage lacks an assertion")
        if set(case.get("coverage_ids", [])) - asserted_cov:
            error(f"{cid}: claimed coverage item lacks an assertion")
        require(case.get("verdict_rules", {}), ["pass", "fail", "inconclusive"], cid)
        if case.get("type") == "automated":
            require(case.get("automation", {}), ["command", "binding_refs"], cid + ".automation")
    if gate == "baseline":
        if policy != DESIGN_POLICY:
            error("New baseline requires project.design_policy=coverage-items-v1 and reviewed coverage items; legacy snapshots remain valid historical records.")
        require(scope, ["objective", "in", "out", "selected_ac_ids", "selected_case_ids", "decision_ref"], "scope")
        refs([scope.get("decision_ref")], "decisions", "scope")
        if stale:
            error("Sources changed/missing: " + ", ".join(sorted(stale)))
        active_ids = set(selected + scope.get("selected_ac_ids", []) + scope.get("selected_risk_ids", [])
                         + scope.get("selected_scenario_ids", []))
        active_cov = [c for c in maps["coverage_items"].values()
                      if set(c.get("ac_ids", [])) & set(scope.get("selected_ac_ids", []))]
        active_ids.update(c["id"] for c in active_cov)
        # Blockers on parent requirements, decisions or source documents also affect selected cases.
        for cid in selected:
            case = cases.get(cid, {})
            for key in ("ac_ids", "risk_ids", "scenario_ids", "coverage_ids"):
                active_ids.update(case.get(key, []))
            active_ids.update(case.get("environment", {}).get("binding_refs", []))
        pending = list(active_ids)
        flat = {rid: row for group in maps.values() for rid, row in group.items()}
        while pending:
            row = flat.get(pending.pop(), {})
            for key in ("requirement_ids", "source_refs", "decision_refs", "ac_ids", "risk_ids", "coverage_ids"):
                for rid in row.get(key, []):
                    if rid not in active_ids:
                        active_ids.add(rid)
                        pending.append(rid)
        for qid, q in maps["questions"].items():
            affected = set(q.get("impact_ids", []))
            if q.get("status") != "resolved" and "baseline" in q.get("blocks", []):
                if not affected or affected & active_ids or "ALL" in affected:
                    error(f"{qid}: unresolved blocker for this baseline")
        selected_cases = [cases[c] for c in selected if c in cases]
        for aid in scope.get("selected_ac_ids", []):
            if not any(aid in c.get("ac_ids", []) and c.get("selection") == "keep" for c in active_cov):
                error(f"{aid}: selected AC has no retained coverage item")
        assertion_cov = {x for c in selected_cases for s in c.get("steps", [])
                         for check in s.get("checks", []) for x in check.get("coverage_ids", [])}
        for cov in active_cov:
            if cov.get("selection") == "keep" and cov["id"] not in assertion_cov:
                error(f"{cov['id']}: retained coverage item has no selected case assertion")
            if cov.get("selection") == "defer" and not cov.get("decision_refs"):
                error(f"{cov['id']}: deferred coverage needs a human decision and residual risk")
        for cid in assertion_cov:
            if maps["coverage_items"].get(cid, {}).get("selection") == "defer":
                error(f"{cid}: selected case assertion claims deferred coverage")
        for sk, ck in (("selected_ac_ids", "ac_ids"), ("selected_risk_ids", "risk_ids"),
                       ("selected_scenario_ids", "scenario_ids")):
            covered = {v for c in selected_cases for v in c.get(ck, [])}
            for rid in scope.get(sk, []):
                if rid not in covered:
                    error(f"scope: selected {rid} has no retained case")
        for sid in scope.get("selected_scenario_ids", []):
            if maps["scenarios"].get(sid, {}).get("selection") != "keep":
                error(f"{sid}: selected scenario must be kept")
        current = snapshot_digest(root)
        completed = set()
        for path in sorted(safe(root, "qa/reviews").glob("*.json")):
            review = read(safe(root, path.relative_to(root)))
            if review.get("artifact_digest") != current:
                continue
            if review.get("independence") not in ("fresh-session", "human"):
                warnings.append(f"{path.name}: self-check is not independent review")
                continue
            require(review, ["reviewer", "session", "at", "rounds"], path.name)
            if review.get("rounds"):
                completed.update(r for r in review["rounds"] if r in ROUNDS)
            if not isinstance(review.get("findings"), list):
                error(f"{path.name}: findings must be a list, possibly empty")
            for finding in review.get("findings", []):
                require(finding, ["id", "round", "issue", "evidence", "proposal"], path.name)
                if finding.get("status") not in ("fixed", "dismissed", "accepted-risk"):
                    error(f"{finding.get('id')}: unresolved finding")
                if not approval_ok(root, finding.get("disposition")):
                    error(f"{finding.get('id')}: needs human disposition evidence")
                if finding.get("status") == "accepted-risk" and not meaningful(finding.get("residual_risk")):
                    error(f"{finding.get('id')}: accepted risk needs residual_risk")
        if set(ROUNDS) - completed:
            error("Missing current independent review rounds: " + ", ".join(sorted(set(ROUNDS) - completed)))
    return {"gate": gate, "artifact_digest": snapshot_digest(root), "errors": errors,
            "warnings": warnings, "note": "Structural checks only; not human approval or product test results."}


def init(args, root):
    root.mkdir(parents=True, exist_ok=True)
    if not shutil.which("git"):
        fail("Install Git locally before initialization; no remote server is required.")
    top = git(root, "rev-parse", "--show-toplevel", check=False)
    if not top.returncode:
        parent = Path(os.fsdecode(top.stdout).strip()).resolve()
        if parent != root:
            if not args.standalone:
                fail("Folder is inside another repository. Use that root, or explicitly pass --standalone.")
            git(root, "init")
    else:
        git(root, "init")
    repo(root)
    marker = safe(root, ".qa-project.json")
    if marker.exists():
        load(root)
        print("Already initialized; existing files preserved.")
        return
    qa = safe(root, "qa")
    if qa.exists() and any(qa.iterdir()):
        fail("Existing nonempty qa/ without project marker; choose/resolve the layout before initialization.")
    for folder in ("cases", "decisions", "reviews", "review-packs", "approvals", "baselines", "runs", "evidence", "tools"):
        safe(root, "qa/" + folder).mkdir(parents=True, exist_ok=True)
    reg = {"schema_version": 1, "project": {"name": args.name or root.name, "owner": "unassigned",
                                         "design_policy": DESIGN_POLICY},
           "scope": {"objective": "", "in": [], "out": [], "selected_ac_ids": [], "selected_risk_ids": [],
                     "selected_scenario_ids": [], "selected_case_ids": [], "decision_ref": None}}
    reg.update({group: [] for group in GROUPS})
    write(safe(root, "qa/registry.json"), reg, exclusive=True)
    docs = {
        "strategy.md": "# 測試策略（草稿）\n\n## 品質目標與風險優先序\n待釐清。\n\n## 範圍與不測範圍\n待選定。\n\n## 層級、類型、方法與自動化\n待規劃。\n\n## 資料、環境與觀測能力\n待確認。\n\n## 進入、退出、缺陷處理與放行證據\n待確認；測試案例核可不代表產品放行。\n\n## 剩餘風險與責任人\n待辨識。\n",
        "plan.md": "# 本輪測試計畫（草稿）\n\n記錄本輪目標、已選 AC（Acceptance Criterion，驗收條件）／風險／情境／TC（Test Case，測試案例）、人力、時程、環境、受測系統版本、工具版本、資料、限制與執行授權。\n\n尚未執行測試。\n",
        "session.md": "# 工作進度\n\n- 階段：資料盤點與需求釐清\n- 已完成：專案結構初始化\n- 下一步：閱讀來源，找出最重要的決策分歧\n- 下一個問題：尚未選定\n- 阻塞與責任人：待盤點\n- 執行結果：尚未執行\n"}
    for name, content in docs.items():
        safe(root, "qa/" + name).write_text(content, encoding="utf-8")
    ignore = safe(root, ".gitignore")
    created_ignore = not ignore.exists()
    if created_ignore:
        ignore.write_text("# Local project exclusions\n.env\n.env.*\n*.pem\n*.key\n*.p12\n*.pfx\n.venv/\nnode_modules/\n__pycache__/\nqa/evidence/raw/\n*.tmp\n", encoding="utf-8")
    shutil.copyfile(Path(__file__), safe(root, "qa/tools/qa_project.py"))
    write(marker, {"schema_version": 1, "tool_version": VERSION, "created_at": now(),
                   "created_gitignore": created_ignore}, exclusive=True)
    render(root)
    print("Initialized local QA project. No remote configured or contacted. Run checkpoint to save a version.")


def iter_files(root, relative):
    path = safe(root, relative)
    if path.is_file():
        if not PRIVATE.search(path.name):
            yield path
        return
    if not path.is_dir():
        fail(f"No such path: {relative}")
    for base, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(base) / d).is_symlink())
        for name in sorted(files):
            p = Path(base) / name
            if p.is_symlink() or PRIVATE.search(name) or name.endswith(".tmp"):
                continue
            if "qa/evidence/raw" in p.relative_to(root).as_posix():
                continue
            yield p


def inventory(root):
    load(root)
    rows = []
    for path in iter_files(root, "."):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("qa/") or rel in (".qa-project.json", ".gitignore"):
            continue
        rows.append({"path": rel, "size": path.stat().st_size, "sha256": file_hash(path)})
    old_path = safe(root, "qa/inventory.json")
    old = {r["path"]: r["sha256"] for r in read(old_path).get("files", [])} if old_path.exists() else {}
    current = {r["path"]: r["sha256"] for r in rows}
    result = {"at": now(), "files": rows, "added": sorted(set(current) - set(old)),
              "removed": sorted(set(old) - set(current)),
              "changed": sorted(k for k in set(old) & set(current) if old[k] != current[k]),
              "note": "Inventory only, not source approval; private filenames, symlinks and generated directories skipped."}
    write(old_path, result)
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, ensure_ascii=False, indent=2))


def coverage_rows(reg, cases):
    """Explicit assertion links only: design references, never executed coverage."""
    selected = set(reg.get("scope", {}).get("selected_case_ids", []))
    selected_ac = set(reg.get("scope", {}).get("selected_ac_ids", []))
    rows = []
    for cov in reg.get("coverage_items", []):
        linked = [cid for cid, case in cases.items() if cid in selected and any(
            cov["id"] in check.get("coverage_ids", [])
            for step in case.get("steps", []) for check in step.get("checks", []))]
        active = bool(selected_ac & set(cov.get("ac_ids", [])))
        state = ("本輪未選" if not active else "暫緩／剩餘風險" if cov.get("selection") == "defer"
                 else "已選案例有斷言引用（待審）" if linked else "缺少已選案例斷言")
        rows.append((cov, linked, state))
    return rows


def render(root):
    reg, cases = load(root)
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    overrides = reg.get("project", {}).get("id_glossary", {})
    if not isinstance(overrides, dict):
        fail("project.id_glossary must be an object")
    def legend(prefixes):
        lines = ["## 編號說明", "", "ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。",
                 "純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。",
                 "非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。", "",
                 "| 前綴 | 英文來源 | 中文意思 | 用途 |", "|---|---|---|---|"]
        for prefix in sorted(prefixes):
            if prefix in overrides:
                entry = overrides[prefix]
                terms = tuple(entry.get(k) for k in ("english", "meaning", "purpose")) if isinstance(entry, dict) else ()
                if len(terms) != 3 or not all(isinstance(t, str) and meaningful(t) for t in terms):
                    terms = ("待確認", "待確認", "請確認本專案定義，不猜測英文來源")
            else:
                terms = ID_TERMS.get(prefix, ("待確認", "待確認", "請確認本專案定義，不猜測英文來源"))
            lines.append("| " + " | ".join(cell(t) for t in (prefix, *terms)) + " |")
        return lines + [""]
    seen = set()
    def save_view(path, lines):
        prefixes = set(re.findall(r"\b([A-Z][A-Z0-9]*)-[A-Za-z0-9_-]+", "\n".join(lines)))
        seen.update(prefixes)
        if prefixes:
            lines = lines[:2] + legend(prefixes) + lines[2:]
        safe(root, path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    spec = ["# 規格與待確認事項", "", "由 registry.json 產生；請修改來源記錄，不直接修改本檔。", ""]
    for title, group in (("需求", "requirements"), ("驗收條件", "acceptance"), ("待確認", "questions")):
        spec += ["## " + title, "", "| ID | 狀態 | 內容 | 依據／責任 |", "|---|---|---|---|"]
        for row in reg[group]:
            basis = row.get("source_refs", []) + row.get("decision_refs", []) if group != "questions" else [row.get("owner"), row.get("due_or_trigger")]
            spec.append(f"| {cell(row['id'])} | {cell(row.get('status'))} | {cell(row.get('text'))} | {cell(basis)} |")
        spec.append("")
    save_view("qa/spec.md", spec)
    trace = ["# 已選範圍追溯", "", "案例連結不代表已執行或已通過。", "", "| 已選項目 | 案例 | 狀態 |", "|---|---|---|"]
    for sk, ck in (("selected_ac_ids", "ac_ids"), ("selected_risk_ids", "risk_ids"), ("selected_scenario_ids", "scenario_ids")):
        for rid in reg["scope"].get(sk, []):
            matched = [c for c in cases.values() if c["id"] in reg["scope"].get("selected_case_ids", []) and rid in c.get(ck, [])]
            trace.append(f"| {cell(rid)} | {cell(', '.join(c['id'] for c in matched) or '缺口')} | {cell(', '.join(c.get('status', '') for c in matched))} |")
    save_view("qa/traceability.md", trace)
    design = ["# 測試設計與探索任務", "", "由 registry.json 產生。斷言引用是設計追溯，仍需審查實際資料與步驟；不是已執行覆蓋率。", "",
              "## 覆蓋項目", "", "| 項目 | 驗收條件 | 方法／內容 | 已選案例斷言 | 狀態／取捨 |",
              "|---|---|---|---|---|"]
    if reg.get("project", {}).get("design_policy") != DESIGN_POLICY:
        design += ["舊版專案尚未採用覆蓋項目；保留草稿編輯，建立新基線前須補齊。", ""]
    for cov, linked, state in coverage_rows(reg, cases):
        design.append("| " + " | ".join(cell(x) for x in (cov["id"], ", ".join(cov.get("ac_ids", [])),
            str(cov.get("technique")) + " / " + str(cov.get("description")), ", ".join(linked) or "無",
            state + " / " + str(cov.get("reason")) + " / " + str(cov.get("residual_risk", "")))) + " |")
    design += ["", "## 探索任務", "", "以下是任務設計；探索紀錄另存 qa/evidence/EXP-*/，不計入正式案例覆蓋或通過率。", ""]
    for charter in reg.get("charters", []):
        design += ["### " + charter["id"] + " — " + charter.get("title", ""), "", "```json",
                   json.dumps(charter, ensure_ascii=False, indent=2), "```", ""]
    save_view("qa/test-design.md", design)
    doc = ["# 測試案例設計", "", "由 cases/*.json 產生。Actual 與執行判定另存 runs；本檔不是執行報告。", ""]
    for cid, case in cases.items():
        doc += [f"## {cid} — {case.get('title', '')}", "", f"狀態：{case.get('status')}；revision：{case.get('revision')}", ""]
        for key in ("purpose", "ac_ids", "risk_ids", "scenario_ids", "coverage_ids", "environment", "preconditions", "data"):
            doc += [f"**{key}**", "", "```json", json.dumps(case.get(key), ensure_ascii=False, indent=2), "```", ""]
        doc += ["| 步驟 | 操作／輸入 | 觀測／時機 | Expected／依據 | 證據 |", "|---|---|---|---|---|"]
        for step in case.get("steps", []):
            expected = "; ".join(f"{c.get('expected')} [{', '.join(c.get('rule_refs', []) + c.get('coverage_ids', []))}]" for c in step.get("checks", []))
            doc.append(f"| {step.get('n')} | {cell(str(step.get('action')) + ' / ' + str(step.get('input')))} | {cell(str(step.get('observe')) + ' / ' + str(step.get('when')))} | {cell(expected)} | {cell(step.get('evidence'))} |")
        for key in ("cleanup", "independence", "verdict_rules", "blockers", "automation"):
            doc += ["", f"**{key}**", "", "```json", json.dumps(case.get(key), ensure_ascii=False, indent=2), "```"]
        doc += [""]
    save_view("qa/test-cases.md", doc)
    catalog = ["# 專案編號字典", "", "由工具預設慣例與 registry.project.id_glossary 產生；修改來源字典後重新 render。", ""]
    catalog += legend(set(ID_TERMS) | set(overrides) | seen)
    safe(root, "qa/id-glossary.md").write_text("\n".join(catalog) + "\n", encoding="utf-8")
    render_html(root, reg, cases)


def render_html(root, reg, cases):
    """Read-only, offline view of explicit references; never infer product coverage."""
    maps = {g: {r["id"]: r for r in reg.get(g, [])} for g in GROUPS}
    maps["cases"] = cases
    labels = {
        "id": "編號", "title": "名稱", "text": "內容", "path": "專案內原始檔",
        "version": "來源版本", "revision": "修訂版次", "sha256": "登錄檔案指紋（SHA-256）",
        "locator": "頁碼／段落", "kind": "類型", "status": "狀態", "note": "備註",
        "excerpt": "來源摘錄（依登錄內容）", "source_refs": "來源資料", "decision_refs": "決策依據",
        "requirement_ids": "對應需求", "confirmation": "確認紀錄", "oracle": "驗收判準",
        "purpose": "測試目的", "level": "測試層級", "type": "執行方式", "ac_ids": "關聯驗收條件",
        "risk_ids": "關聯風險", "scenario_ids": "關聯情境", "environment": "測試環境",
        "target": "受測環境／對象", "build_binding": "受測版本辨識", "tools": "工具與版本",
        "binding_refs": "操作／觀測依據", "preconditions": "前置條件", "action": "操作",
        "verify": "確認方式", "data": "測試資料", "name": "名稱", "value": "值", "unit": "單位",
        "basis": "依據", "input": "輸入", "observe": "觀察點", "when": "判定時機",
        "evidence": "需保存的證據", "checks": "預期結果與規則", "expected": "預期結果",
        "rule_refs": "判準依據", "cleanup": "清理與復原", "independence": "獨立重跑方式",
        "verdict_rules": "判定條件（不是實際結果）", "pass": "通過條件", "fail": "失敗條件",
        "inconclusive": "無法判定條件", "blockers": "阻塞問題", "automation": "自動化資料",
        "provenance": "產生依據", "statement": "決策內容", "by": "決策人", "at": "時間",
        "evidence_ref": "決策記錄原檔", "affected_ids": "影響項目", "impact_ids": "影響項目",
        "owner": "責任人", "due_or_trigger": "確認時點", "blocks": "阻塞階段",
        "failure": "失敗情境", "impact": "影響", "priority": "優先度", "rationale": "理由",
        "likelihood": "發生可能性", "uncertainty": "不確定性", "residual_risk": "剩餘風險",
        "description": "情境描述", "category": "類型", "selection": "選取結果", "reason": "理由",
        "tolerance": "容差", "supersedes": "替代舊項目", "merged_into": "合併目標",
        "coverage_ids": "覆蓋項目", "technique": "測試設計方法", "origin": "候選情境產生方式",
        "applies_when": "判準適用條件", "limitations": "判準限制", "relation": "已確認的比較關係",
        "reference_refs": "比較參考資料（不是自動採納的正確答案）", "mission": "探索目的",
        "timebox_minutes": "探索時間上限（分鐘）", "actions": "探索操作與觀察", "scope": "範圍",
        "stop_conditions": "停止條件", "question_ids": "待釐清問題",
    }
    ref_groups = {"source_refs": "sources", "binding_refs": "sources", "decision_refs": "decisions",
                  "decision_ref": "decisions", "requirement_ids": "requirements", "ac_ids": "acceptance",
                  "rule_refs": "acceptance", "risk_ids": "risks", "scenario_ids": "scenarios",
                  "case_ids": "cases", "blockers": "questions", "merged_into": "scenarios",
                  "coverage_ids": "coverage_items", "question_ids": "questions", "reference_refs": "sources"}
    for key in ("ac", "risk", "scenario", "case"):
        ref_groups["selected_" + key + "_ids"] = ref_groups[key + "_ids"]
    backlinks, routes, gaps = {}, {}, {}
    direct_backlinks = {}
    def collect_refs(v, key=""):
        if isinstance(v, dict):
            for k, x in v.items():
                yield from collect_refs(x, k)
        elif isinstance(v, list):
            for x in v:
                yield from collect_refs(x, key)
        elif key in ref_groups and isinstance(v, str):
            yield ref_groups[key], v
    for group, records in maps.items():
        for rid, record in records.items():
            for target in collect_refs(record):
                direct_backlinks.setdefault(target, set()).add((group, rid))

    def ids(value):
        return value if isinstance(value, list) else []

    def anchor(group, rid):
        return group + "-" + str(rid).encode("utf-8").hex()

    def e(value):
        return escape(str(value), quote=True)

    def link(group, rid):
        if rid not in maps.get(group, {}):
            return '<span class="gap">' + e(rid) + '（未登錄）</span>'
        return '<a href="#' + anchor(group, rid) + '">' + e(rid) + '</a>'

    def auto_link(rid):
        for group in maps:
            if rid in maps[group]:
                return link(group, rid)
        return e(rid)

    def file_link(value, allow_fragment=False):
        raw = str(value)
        rel, _, fragment = raw.partition("#") if allow_fragment else (raw, "", "")
        try:
            p = safe(root, rel)
            if not p.is_file():
                raise ValueError("missing")
        except (ValueError, OSError):
            return '<span class="gap">' + e(raw) + '（檔案不可用／路徑不安全）</span>'
        url = "../" + quote(Path(rel).as_posix(), safe="/")
        if fragment:
            url += "#" + quote(fragment, safe="")
        return '<a href="' + e(url) + '">' + e(raw) + '</a>'

    def value(v, key=""):
        if v is None or v == "":
            return '<span class="muted">尚未提供</span>'
        if isinstance(v, list):
            return '<ul>' + ''.join('<li>' + value(x, key) + '</li>' for x in v) + '</ul>' if v else '無列項'
        if isinstance(v, dict):
            return '<dl>' + ''.join('<dt>' + e(labels.get(k, k)) + '</dt><dd>' + value(x, k) + '</dd>'
                                   for k, x in v.items()) + '</dl>' if v else '尚未提供'
        if key in ref_groups:
            return link(ref_groups[key], str(v))
        if key in ("impact_ids", "affected_ids", "supersedes", "basis"):
            return auto_link(str(v))
        if key in ("path", "evidence_ref"):
            return file_link(v, allow_fragment=key == "evidence_ref")
        return e(v)

    def touch(cid, group, rid):
        backlinks.setdefault((group, rid), set()).add(cid)
        if rid not in maps.get(group, {}):
            gaps[cid].add((group, rid))

    def source(cid, sid, role, chain):
        touch(cid, "sources", sid)
        row = (sid, role, tuple(chain + [("sources", sid)]))
        if row not in routes[cid]:
            routes[cid].append(row)

    def rule(cid, group, rid, role, chain):
        touch(cid, group, rid)
        row = maps[group].get(rid, {})
        chain = chain + [(group, rid)]
        for sid in ids(row.get("source_refs")):
            source(cid, sid, role, chain)
        for did in ids(row.get("decision_refs")):
            touch(cid, "decisions", did)
        for sid in ids((row.get("oracle") or {}).get("reference_refs")):
            source(cid, sid, "比較參考資料；判準以已確認關係為準", chain)
        if group == "acceptance":
            for req in ids(row.get("requirement_ids")):
                rule(cid, "requirements", req, role, chain)

    for cid, case in cases.items():
        routes[cid], gaps[cid] = [], set()
        base = [("cases", cid)]
        for aid in ids(case.get("ac_ids")):
            rule(cid, "acceptance", aid, "案例宣告關聯", base)
        for step in case.get("steps", []):
            for check in step.get("checks", []):
                for aid in ids(check.get("rule_refs")):
                    rule(cid, "acceptance", aid, "預期結果依據：步驟 " + str(step.get("n", "?")), base)
        cov_ids = set(ids(case.get("coverage_ids")))
        cov_ids.update(x for step in case.get("steps", []) for check in step.get("checks", [])
                       for x in ids(check.get("coverage_ids")))
        for cov_id in sorted(cov_ids):
            touch(cid, "coverage_items", cov_id)
            for aid in ids(maps["coverage_items"].get(cov_id, {}).get("ac_ids")):
                rule(cid, "acceptance", aid, "覆蓋項目的規則依據", base + [("coverage_items", cov_id)])
        for sid in ids(case.get("scenario_ids")):
            for src in ids(maps["scenarios"].get(sid, {}).get("source_refs")):
                source(cid, src, "候選情境線索；不是產品判準", base + [("scenarios", sid)])
        for field, role in (("environment", "操作／觀測依據"), ("automation", "自動化操作依據")):
            for sid in ids((case.get(field) or {}).get("binding_refs")):
                source(cid, sid, role, base)
        for data in case.get("data", []):
            basis = data.get("basis")
            if isinstance(basis, str) and basis in maps["sources"]:
                source(cid, basis, "測試資料依據", base)
        for field, group in (("risk_ids", "risks"), ("scenario_ids", "scenarios"), ("blockers", "questions")):
            for rid in ids(case.get(field)):
                touch(cid, group, rid)

    def case_links(group, rid):
        linked = sorted(backlinks.get((group, rid), set()))
        return '、'.join(link("cases", c) for c in linked) if linked else '<span class="muted">目前沒有案例引用</span>'

    def related_links(group, rid):
        related = sorted(direct_backlinks.get((group, rid), set()))
        return ('<h4>反查直接引用記錄</h4><p>' + '、'.join(link(g, r) for g, r in related) + '</p>') if related else ''

    def source_links(cid):
        return '、'.join(link("sources", sid) for sid in sorted({r[0] for r in routes[cid]})) or '未連結來源文件'

    health = {}
    for sid, src in maps["sources"].items():
        try:
            p = safe(root, src.get("path", ""))
            if not p.is_file():
                raise ValueError("missing")
            actual = file_hash(p)
            note = "未登錄檔案指紋" if not src.get("sha256") else (
                "檔案指紋相符" if actual == src["sha256"] else "來源已變更，需重新閱讀及評估影響")
            health[sid] = (note, actual)
        except (ValueError, OSError):
            health[sid] = ("來源檔案不可用／路徑不安全", None)

    css = """
    :root{--ink:#172d43;--muted:#50657a;--line:#d7e3ec;--blue:#085786;--teal:#007d80}
    *{box-sizing:border-box}html{scroll-padding-top:5rem}body{margin:0;background:#f4f7fa;color:var(--ink);font:16px/1.65 system-ui,'Noto Sans TC',sans-serif}
    a{color:var(--blue);text-underline-offset:3px}a:hover{color:var(--teal)}a:focus-visible{outline:3px solid #ef9b32;outline-offset:3px}
    header{background:#102f4b;color:white;padding:3rem max(5vw,calc((100vw - 1240px)/2))}header h1{font-size:clamp(1.7rem,4vw,2.7rem);margin:.4rem 0}header p{max-width:80ch;color:#e1edf5}
    .eyebrow{letter-spacing:.14em;font-size:.8rem;color:#86e1dc}.meta{font-size:.85rem;overflow-wrap:anywhere}
    nav{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;padding:.8rem 5vw;background:white;border-bottom:1px solid var(--line)}nav a{font-weight:650}
    main{max-width:1340px;margin:auto;padding:1.5rem clamp(1rem,4vw,3rem) 4rem}section{margin:2rem 0}h2{font-size:1.5rem}h3{font-size:1.2rem;margin:.2rem 0 1rem}h4{margin:1.2rem 0 .5rem}
    .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.stat{padding:1rem 1.4rem;background:white;border:1px solid var(--line);border-top:4px solid var(--teal);border-radius:10px}.stat b{font-size:2rem;display:block}
    .record{background:white;border:1px solid var(--line);border-radius:12px;padding:1.5rem;margin:1rem 0;overflow-wrap:anywhere;scroll-margin-top:5rem}.record:target{outline:3px solid #e89b35;background:#fffdf6}
    .scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:white}th,td{border:1px solid var(--line);padding:.65rem .8rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#e9f1f7;font-weight:650}.steps{min-width:800px}.steps td{min-width:100px}.steps td:first-child{min-width:45px}
    dl{display:grid;grid-template-columns:minmax(100px,180px) minmax(0,1fr);gap:.45rem 1rem;margin:.4rem 0}dt{font-weight:650;color:var(--muted)}dd{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}dd dl{font-size:.95em}ul{padding-left:1.3rem;margin:.25rem 0}li{margin:.35rem 0}
    .muted{color:var(--muted)}.gap{color:#9d3d05;font-weight:650}.notice{border-left:4px solid #e59a2b;background:#fff5e5;padding:.8rem 1rem}.badge{display:inline-block;padding:.15rem .55rem;background:#e7f4f3;color:#075d60;border-radius:6px;font-size:.85rem}.back{font-size:.85rem;margin-top:1rem}
    .document{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}summary{cursor:pointer;font-weight:650;padding:.6rem 0}footer{padding:1rem;color:var(--muted);border-top:1px solid var(--line)}
    @media(max-width:650px){.stats{gap:.4rem}.stat{padding:.7rem}.stat b{font-size:1.4rem}dl{grid-template-columns:1fr;gap:.1rem}.record{padding:1rem}dd{margin-bottom:.5rem}nav{position:static}}
    @media print{body{background:white;font-size:10pt}header{background:white;color:#172d43;padding:0}header p,.eyebrow{color:#172d43}nav,.back{display:none}main{padding:0;max-width:none}.record{border-radius:0}a{color:#172d43}.scroll{overflow:visible}.steps{min-width:0}.steps td{min-width:0}tr{break-inside:avoid}h2,h3,h4{break-after:avoid}details{display:block}}
    """
    project = reg.get("project", {})
    title = project.get("name", "測試專案")
    overrides = project.get("id_glossary", {})

    def terms_for(prefix):
        if prefix in overrides:
            custom = overrides[prefix]
            candidate = tuple(custom.get(k) for k in ("english", "meaning", "purpose")) if isinstance(custom, dict) else ()
            return candidate if len(candidate) == 3 and all(isinstance(t, str) and meaningful(t) for t in candidate) else ("待確認", "待確認", "請確認本專案定義")
        return ID_TERMS.get(prefix, ("待確認", "待確認", "請確認本專案定義"))

    prefix_note = '；'.join(p + '＝' + terms_for(p)[0] + '（' + terms_for(p)[1] + '）' for p in ("SRC", "TC"))
    out = ['<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<title>' + e(title) + '｜來源與測試案例</title><style>' + css + '</style></head><body>',
           '<header id="top"><div class="eyebrow">GENAI TEST STRATEGY · PROJECT REPORT</div>',
           '<h1>' + e(title) + '</h1><p>來源與測試案例 · 雙向追溯閱讀報告</p>',
           '<p>' + e(prefix_note) + '。點選編號查看完整內容，再由來源反查相關案例。</p>',
           '<div class="meta">產生時間：' + e(now()) + ' · 工具版本：' + VERSION + '</div></header>',
           '<nav aria-label="報告章節"><a href="#sources">來源清單</a><a href="#cases">案例清單</a>',
           '<a href="#coverage">設計覆蓋</a><a href="#exploration">探索任務</a>',
           '<a href="#rules">需求與驗收</a><a href="#other">風險與待確認</a><a href="#glossary">編號說明</a><a href="#documents">其他成果</a></nav><main>',
           '<div class="notice">這是設計資料的閱讀快照。連結表示已登錄的引用，不代表已覆蓋、已核可或已執行；本頁不產生實際測試結果。</div>',
           '<div class="stats">' + ''.join('<div class="stat"><b>' + str(n) + '</b>' + label + '</div>' for n, label in
                                           ((len(maps["sources"]), "來源資料"), (len(cases), "測試案例"),
                                            (sum(q.get("status") != "resolved" for q in maps["questions"].values()), "未決問題"))) + '</div>']
    out += ['<section id="glossary"><h2>編號說明</h2><p>ID＝Identifier（識別碼）。數字後綴是各類流水號，不代表優先度、版本、核可或結果；文字後綴是專案標籤。</p>',
            '<details><summary>查看英文來源、中文意思與用途</summary><table><thead><tr><th>前綴</th><th>英文來源</th><th>意思</th><th>用途</th></tr></thead><tbody>']
    prefixes = set(ID_TERMS) | set(overrides) | {str(r).split("-", 1)[0] for rows in maps.values() for r in rows}
    for prefix in sorted(prefixes):
        terms = terms_for(prefix)
        out.append('<tr>' + ''.join('<td>' + e(x) + '</td>' for x in (prefix, *terms)) + '</tr>')
    out += ['</tbody></table></details></section>', '<section id="sources"><h2>來源清單</h2>',
            '<p>normative＝規格依據；harness＝操作／觀測指南；observation＝現況觀察；experience＝經驗線索（不提供 Expected）。指紋相符僅表示檔案未改變，不代表內容已確認。</p>',
            '<div class="scroll"><table><thead><tr><th>來源編號</th><th>名稱／檔案</th><th>類型／版本／狀態</th><th>引用案例</th></tr></thead><tbody>']
    for sid, src in maps["sources"].items():
        out.append('<tr><td>' + link("sources", sid) + '</td><td>' + e(src.get("title") or src.get("path", "尚未提供")) +
                   '</td><td>' + e(' / '.join(str(src.get(k) or '未提供') for k in ("kind", "version", "status"))) +
                   '</td><td>' + case_links("sources", sid) + '</td></tr>')
    out += ['</tbody></table></div>' if maps["sources"] else '</tbody></table></div><p>尚未登錄來源。</p>']
    for sid, src in maps["sources"].items():
        out += ['<article class="record" id="' + anchor("sources", sid) + '" data-record-id="' + e(sid) + '"><h3>' + e(sid) + ' · ' + e(src.get("title") or src.get("path", "來源")) + '</h3>',
                value({k: v for k, v in src.items() if k not in ("id", "title")}),
                '<p class="notice">檔案檢查：' + e(health[sid][0]) + '</p>',
                '<h4>反查引用案例</h4><p>' + case_links("sources", sid) + '</p>' + related_links("sources", sid) + '<p class="back"><a href="#sources">返回來源清單</a></p></article>']
    selected = set(reg.get("scope", {}).get("selected_case_ids", []))
    out += ['</section><section id="cases"><h2>測試案例清單</h2><p>draft＝草稿；blocked＝有阻塞；ready＝設計就緒；retired＝停用。人工執行的完整步驟列在各案例內。</p>',
            '<div class="scroll"><table><thead><tr><th>案例編號</th><th>標題</th><th>狀態／本輪範圍</th><th>參考來源</th></tr></thead><tbody>']
    for cid, case in cases.items():
        out.append('<tr><td>' + link("cases", cid) + '</td><td>' + e(case.get("title", "")) + '</td><td>' + e(case.get("status", "未提供")) +
                   (' / 本輪已選' if cid in selected else ' / 本輪未選') + '</td><td>' + source_links(cid) + '</td></tr>')
    out += ['</tbody></table></div>' if cases else '</tbody></table></div><p>尚未建立測試案例。</p>']
    for cid, case in cases.items():
        tail = ("cleanup", "independence", "verdict_rules", "blockers", "automation", "provenance")
        out += ['<article class="record" id="' + anchor("cases", cid) + '" data-record-id="' + e(cid) + '"><h3>' + e(cid) + ' · ' + e(case.get("title", "")) + '</h3>',
                value({k: v for k, v in case.items() if k not in ("id", "title", "steps", "actual", "result", *tail)}), '<h4>完整操作步驟</h4>',
                '<p>下表數字為操作順序；Expected 是預期結果，須由已確認規則支持。</p>',
                '<div class="scroll"><table class="steps"><thead><tr>' + ''.join('<th>' + s + '</th>' for s in
                    ("步驟", "操作／輸入", "觀察／判定時機", "預期結果／規則", "證據")) + '</tr></thead><tbody>']
        for step in case.get("steps", []):
            cells = [e(step.get("n", "?")), value({k: step.get(k) for k in ("action", "input")}),
                     value({k: step.get(k) for k in ("observe", "when")}),
                     value(step.get("checks")) if step.get("checks") else '此步驟未列產品斷言', value(step.get("evidence"))]
            out.append('<tr>' + ''.join('<td>' + c + '</td>' for c in cells) + '</tr>')
        out += ['</tbody></table></div>', value({k: case[k] for k in tail if k in case}), '<h4>參考來源與引用路徑</h4>']
        if routes[cid]:
            out.append('<ul>')
            for sid, role, chain in routes[cid]:
                out.append('<li><span class="badge">' + e(role) + '</span> ' + ' → '.join(link(g, r) for g, r in chain) + '</li>')
            out.append('</ul>')
        else:
            out.append('<p class="notice">未連結來源文件；請檢視規則／決策依據，不能自行補推來源。</p>')
        if gaps[cid]:
            out.append('<p class="gap">引用缺口：' + '、'.join(link(g, r) for g, r in sorted(gaps[cid])) + '</p>')
        out += ['<p class="back"><a href="#cases">返回案例清單</a> · <a href="#sources">查看全部來源</a></p></article>']
    out.append('</section>')
    out += ['<section id="coverage"><h2>設計覆蓋與剩餘風險</h2>',
            '<p class="notice">此表只顯示已選案例是否引用覆蓋項目，需審查輸入、初態與斷言是否真正承接。不是實際執行覆蓋率；執行結果與證據另見 runs。</p>']
    if project.get("design_policy") != DESIGN_POLICY:
        out.append('<p class="gap">舊版專案尚未採用覆蓋項目；建立新基線前須補齊。</p>')
    out.append('<div class="scroll"><table><thead><tr><th>覆蓋項目</th><th>驗收條件</th><th>方法／內容</th><th>已選案例斷言</th><th>狀態</th></tr></thead><tbody>')
    for cov, linked, state in coverage_rows(reg, cases):
        out.append('<tr><td>' + link("coverage_items", cov["id"]) + '</td><td>' + value(cov.get("ac_ids"), "ac_ids") +
                   '</td><td>' + e(str(cov.get("technique")) + ' / ' + str(cov.get("description"))) + '</td><td>' +
                   ('、'.join(link("cases", cid) for cid in linked) or '無') + '</td><td>' + e(state) + '</td></tr>')
    out.append('</tbody></table></div></section>')
    for section, heading, groups in (("rules", "需求、驗收條件與決策", ("requirements", "acceptance", "decisions")),
                                    ("other", "風險、候選情境與待確認事項", ("risks", "scenarios", "questions")),
                                    ("coverage-details", "覆蓋項目詳情", ("coverage_items",)),
                                    ("exploration", "探索任務設計（非執行結果）", ("charters",))):
        out.append('<section id="' + section + '"><h2>' + heading + '</h2>')
        if section == "exploration":
            out.append('<p>任務可在缺少部分產品判準時先設計；操作與環境仍需有依據。探索紀錄另存 qa/evidence/EXP-*/，不取代正式案例及其驗證結果。</p>')
        for group in groups:
            for rid, row in maps[group].items():
                out += ['<article class="record" id="' + anchor(group, rid) + '" data-record-id="' + e(rid) + '"><h3>' + e(rid) + '</h3>',
                        value({k: v for k, v in row.items() if k != "id"}), '<h4>相關案例</h4><p>' + case_links(group, rid) +
                        '</p>' + related_links(group, rid) + '<p class="back"><a href="#cases">返回案例清單</a></p></article>']
        out.append('</section>')
    out += ['<section id="documents"><h2>其他成果與本輪範圍</h2>', value(reg.get("scope", {}))]
    for filename, label in (("strategy.md", "測試策略"), ("plan.md", "本輪計畫"), ("session.md", "工作進度")):
        p = safe(root, "qa/" + filename)
        if p.is_file():
            out += ['<details class="record"><summary>' + label + '</summary><pre class="document">' + e(p.read_text(encoding="utf-8")) + '</pre></details>']
    out += ['<p>原有文件仍保留：' + ' · '.join(file_link("qa/" + f) for f in
            ("spec.md", "test-design.md", "test-cases.md", "traceability.md", "id-glossary.md", "registry.json")) + '</p></section>',
            '<footer>本頁由專案記錄產生，請修改原始記錄後重新 render，不直接編輯本頁。可離線閱讀；以瀏覽器尋找功能搜尋編號或文字。來源原檔連結需保留專案相對目錄；僅分享此 HTML 仍可使用頁內雙向連結。<a href="#top">回到頂端</a></footer></main></body></html>']
    safe(root, "qa/report.html").write_text(''.join(out), encoding="utf-8")


def checkpoint(args, root):
    reg, _ = load(root)
    repo(root)
    if git(root, "diff", "--cached", "--name-only", "-z").stdout:
        fail("Existing staged changes preserved. Commit or unstage them yourself before checkpoint.")
    if args.tag and git(root, "check-ref-format", "refs/tags/" + args.tag, check=False).returncode:
        fail("Invalid Git tag name; no files staged.")
    if args.tag and git(root, "show-ref", "--verify", "refs/tags/" + args.tag, check=False).returncode == 0:
        fail("Tag already exists; never move a published baseline label.")
    paths = [".qa-project.json", "qa"] + args.include
    # Registered source/evidence paths are explicit project inputs, not a blanket git add.
    paths += [s["path"] for s in reg.get("sources", []) if s.get("path")]
    paths += list(artifacts(root)["decision_evidence_hashes"])
    if read(safe(root, ".qa-project.json")).get("created_gitignore"):
        paths.append(".gitignore")
    names = set()
    for relative in paths:
        path = safe(root, relative)
        # Allow deletion of explicitly tracked paths without staging unrelated work.
        if path.exists():
            for file in iter_files(root, relative):
                rel = file.relative_to(root).as_posix()
                if git(root, "check-ignore", "-q", "--", rel, check=False).returncode != 0:
                    names.add(rel)
        for tracked in git(root, "ls-files", "-z", "--", relative).stdout.split(b"\0"):
            if tracked:
                rel = os.fsdecode(tracked)
                safe(root, rel)
                if PRIVATE.search(Path(rel).name):
                    fail(f"Refusing known private filename already tracked: {rel}")
                names.add(rel)
    if not names:
        fail("No eligible files. Inspect ignore rules and explicit --include paths.")
    for name in sorted(names):
        git(root, "add", "-A", "--", name)
    if git(root, "diff", "--cached", "--quiet", check=False).returncode == 0:
        print("No changes to checkpoint.")
        return
    identity = []
    if git(root, "config", "user.name", check=False).returncode:
        identity += ["-c", "user.name=QA workflow"]
    if git(root, "config", "user.email", check=False).returncode:
        identity += ["-c", "user.email=qa-workflow@localhost"]
    git(root, *identity, "commit", "-m", args.message)
    if args.tag:
        git(root, *identity, "tag", "-a", args.tag, "-m", args.message)
    print(git(root, "rev-parse", "HEAD").stdout.decode().strip())


def valid_id(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        fail("Use a unique ID containing letters, digits, dash or underscore.")
    return value


def review_pack(args, root):
    data = artifacts(root)
    pack = safe(root, "qa/review-packs/" + valid_id(args.id))
    if pack.exists():
        fail("Review pack already exists; use a new ID.")
    reg = data["registry"]
    # Experience supplies candidate ideas, never Expected. Only explicitly adopted comparison
    # references accompany derived oracles; arbitrary observed behavior stays out.
    comparison_ids = {sid for ac in reg.get("acceptance", []) if ac.get("status") == "confirmed"
                      and ac.get("decision_refs") and (ac.get("oracle") or {}).get("kind") == "derived"
                      for sid in ac["oracle"].get("reference_refs", [])}
    permitted = {s["id"] for s in reg["sources"] if s.get("kind") in ("normative", "harness", "experience")
                 or s["id"] in comparison_ids}
    filtered = json.loads(json.dumps(data))
    filtered["registry"]["sources"] = [s for s in reg["sources"] if s["id"] in permitted]
    packet = {"artifact_digest": digest(data), "created_at": now(), "review_input": filtered,
              "handoff": {"protocol_version": 1, "target_skill": "genai-test-review",
                          "design_tool_version": VERSION},
              "comparison_reference_ids": sorted(comparison_ids),
              "instruction": "Reload confirmed rules, decisions, bindings and coverage items. Experience sources suggest scenarios only. Comparison artifacts support only the explicitly confirmed relation; observed behavior is not automatically correct."}
    write(pack / "packet.json", packet, exclusive=True)
    (pack / "PROMPT.md").write_text(
        "請使用 genai-test-review，在新工作階段依 packet.json 審查測試案例。重讀已確認規格、選定範圍、操作介面依據及該 Skill 的審查準則。\n"
        "沿用原專案與版本，不執行 init、不重問規格概況／版控、不重設釐清額度；四輪是檢查種類，不是四輪訪談。\n"
        "只新增本次審查紀錄，不改來源、registry、案例、scope、session 或舊審查；產品決策缺口交回 genai-test-strategy。\n"
        "artifact_digest 綁完整設計；review_input 可能過濾來源，不得用其子集重新計算並替換 digest。核對原始來源 hash 與目標版本。\n"
        "分四輪：traceability、executable、coverage、consistency。逐輪列 Finding：ID、case_ids、rule_refs、issue、evidence、proposal。\n"
        "覆蓋輪同時檢查已選 AC／風險／情境與保留 COV：分區、邊界、組合、初態及轉移是否完整；案例的輸入與斷言是否真的承接。暫緩項目查決策與剩餘風險。\n"
        "共用／推導判準須查人的採納、適用條件與限制；experience 僅供候選線索，comparison_reference_ids 僅供已確認的比較關係。EXP 是探索計畫，不算正式案例覆蓋。\n"
        "缺少產品規則則列待釐清，不得新增 Expected。不得從程式碼、產碼對話、目前 UI 行為推導 Expected。\n"
        "只處理選定範圍；記錄 reviewer、session、model（不知則 unknown）、at、independence 與 artifact_digest。\n"
        "同對話換 Skill 仍標 same-session。尚未執行產品測試，不可填 Actual 或 Pass。只將真正完成的輪次寫入 rounds，讀不到來源或未檢完範圍則記 limitations。\n"
        "將 review 放在 qa/reviews/<新 ID>.json，findings 保持 open 交人處置。返回設計端修正後須以新版本重審，不改舊 review 的 digest。\n"
        "若審查 Skill 尚不可用，可把本包與完整來源交由人審查；不假稱已安裝或已完成四輪。\n",
        encoding="utf-8")
    print(str(pack))


def baseline(args, root):
    report = inspect(root, "baseline")
    if report["errors"]:
        fail("Baseline blocked:\n" + "\n".join(report["errors"]))
    approval = read(safe(root, args.approval))
    if not approval_ok(root, approval):
        fail("Baseline requires actual human approval with local decision evidence.")
    reg, _ = load(root)
    if approval.get("artifact_digest") != report["artifact_digest"]:
        fail("Approval is stale or not bound to the exact current content.")
    if sorted(approval.get("case_ids", [])) != sorted(reg["scope"]["selected_case_ids"]):
        fail("Approval must cover exactly the selected case IDs.")
    path = safe(root, "qa/baselines/" + valid_id(args.id) + ".json")
    reviews = [read(p) for p in safe(root, "qa/reviews").glob("*.json")]
    write(path, {"id": args.id, "created_at": now(), "artifact_digest": report["artifact_digest"],
                 "approval": approval, "snapshot": artifacts(root),
                 "reviews": [r for r in reviews if r.get("artifact_digest") == report["artifact_digest"]],
                 "meaning": "Human-approved case baseline; not product release approval or execution evidence."}, exclusive=True)
    print(str(path))


def start_run(args, root):
    repo(root)
    reg, cases = load(root)
    if args.case not in cases:
        fail("Unknown case ID")
    if not meaningful(args.sut_version) or not meaningful(args.environment):
        fail("Identify the actual tested SUT build/artifact and execution environment.")
    data = artifacts(root)
    case = cases[args.case]
    path = safe(root, "qa/runs/" + valid_id(args.id) + ".json")
    head = git(root, "rev-parse", "HEAD", check=False)
    run = {"id": args.id, "created_at": now(), "status": "NOT_RUN", "case_id": args.case,
           "artifact_digest": digest(data), "design_snapshot": data, "case_digest": digest(case), "case_snapshot": case,
           "registry_snapshot": reg, "registry_digest": digest(reg), "sut_version": args.sut_version, "environment": args.environment,
           "git_head": head.stdout.decode().strip() if head.returncode == 0 else None,
           "git_status": os.fsdecode(git(root, "status", "--porcelain=v1", "--untracked-files=all").stdout),
           "started_at": None, "finished_at": None, "operator": None,
           "steps": [{"n": s["n"], "actual": None, "status": "NOT_RUN", "at": None, "evidence": []} for s in case.get("steps", [])],
           "notes": "No test has been executed by start-run. Bind a real build; preserve relevant dirty changes separately."}
    write(path, run, exclusive=True)
    print(str(path))


def check_run(args, root):
    run = read(safe(root, "qa/runs/" + valid_id(args.id) + ".json"))
    errors = []
    allowed = {"NOT_RUN", "PASS", "FAIL", "BLOCKED", "INCONCLUSIVE"}
    if run.get("status") not in allowed:
        errors.append("Invalid run status")
    if digest(run.get("case_snapshot")) != run.get("case_digest"):
        errors.append("Case snapshot changed after run creation")
    if digest(run.get("registry_snapshot")) != run.get("registry_digest"):
        errors.append("Registry snapshot changed after run creation")
    if digest(run.get("design_snapshot")) != run.get("artifact_digest"):
        errors.append("Design snapshot changed after run creation")
    if run.get("design_snapshot", {}).get("cases", {}).get(run.get("case_id")) != run.get("case_snapshot"):
        errors.append("Case snapshot does not match frozen design")
    if run.get("design_snapshot", {}).get("registry") != run.get("registry_snapshot"):
        errors.append("Registry snapshot does not match frozen design")
    expected_ns = [s["n"] for s in run.get("case_snapshot", {}).get("steps", [])]
    if [s.get("n") for s in run.get("steps", [])] != expected_ns:
        errors.append("Run step numbers differ from frozen case")
    for step in run.get("steps", []):
        status = step.get("status")
        if status not in allowed:
            errors.append(f"Step {step.get('n')}: invalid status")
        if status != "NOT_RUN":
            for key in ("actual", "at"):
                if not meaningful(step.get(key)):
                    errors.append(f"Step {step.get('n')}: missing {key}")
        if status in ("PASS", "FAIL") and not step.get("evidence"):
            errors.append(f"Step {step.get('n')}: PASS/FAIL requires evidence")
        for evidence in step.get("evidence", []):
            p = safe(root, evidence.get("path", ""))
            if not p.is_file() or file_hash(p) != evidence.get("sha256"):
                errors.append(f"Step {step.get('n')}: evidence missing or hash mismatch")
    if run.get("status") == "PASS":
        if not run.get("steps") or any(s.get("status") != "PASS" for s in run["steps"]):
            errors.append("Run cannot PASS unless every step passed")
        if run.get("case_snapshot", {}).get("status") != "ready":
            errors.append("Blocked/draft case cannot produce a formal PASS")
    if run.get("status") == "FAIL" and not any(s.get("status") == "FAIL" for s in run.get("steps", [])):
        errors.append("Run FAIL requires a failed step")
    if run.get("status") != "NOT_RUN":
        for key in ("started_at", "finished_at", "operator"):
            if not meaningful(run.get(key)):
                errors.append("Missing " + key)
    report = {"errors": errors, "note": "Checks record completeness only; evidence must still be reviewed."}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("init", "inventory", "check", "render", "digest", "checkpoint", "review-pack", "baseline", "start-run", "check-run"):
        p = sub.add_parser(name)
        p.add_argument("root", help="Accessible local project root (quote paths containing spaces)")
        if name == "init":
            p.add_argument("--name")
            p.add_argument("--standalone", action="store_true")
        if name == "check":
            p.add_argument("--gate", choices=["draft", "baseline"], default="draft")
        if name == "checkpoint":
            p.add_argument("-m", "--message", required=True)
            p.add_argument("--include", action="append", default=[])
            p.add_argument("--tag")
        if name in ("review-pack", "baseline", "start-run", "check-run"):
            p.add_argument("--id", required=True)
        if name == "baseline":
            p.add_argument("--approval", required=True, help="Project-relative human approval JSON")
        if name == "start-run":
            p.add_argument("--case", required=True)
            p.add_argument("--sut-version", required=True)
            p.add_argument("--environment", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    try:
        if args.cmd == "init": init(args, root)
        elif args.cmd == "inventory": inventory(root)
        elif args.cmd == "render": render(root)
        elif args.cmd == "digest": print(snapshot_digest(root))
        elif args.cmd == "check":
            report = inspect(root, args.gate)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return int(bool(report["errors"]))
        elif args.cmd == "checkpoint": checkpoint(args, root)
        elif args.cmd == "review-pack": review_pack(args, root)
        elif args.cmd == "baseline": baseline(args, root)
        elif args.cmd == "start-run": start_run(args, root)
        elif args.cmd == "check-run": return int(check_run(args, root))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
