#!/usr/bin/env python3
"""Local QA records and version checkpoints. Python 3.10+, stdlib + Git only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

VERSION = "1.1.0"
ID_TERMS = {
    "SRC": ("Source", "資料來源", "追蹤文件、操作指南或其他依據"),
    "REQ": ("Requirement", "需求", "追蹤單一產品需求"),
    "AC": ("Acceptance Criterion", "驗收條件", "定義可觀測且可判定的產品條件"),
    "Q": ("Question", "待釐清問題", "追蹤未決事項、責任人與確認時點"),
    "DEC": ("Decision", "決策", "記錄人的決定與依據"),
    "RISK": ("Risk", "風險", "追蹤失敗情境、影響與取捨"),
    "SC": ("Scenario", "測試情境", "表示待選或已選的測試情境"),
    "TC": ("Test Case", "測試案例", "保存完整前置、步驟、判準與證據要求"),
    "REV": ("Review", "審查紀錄", "記錄特定版本的案例審查"),
    "F": ("Finding", "審查發現", "追蹤具體問題與處置"),
    "APP": ("Approval", "核可紀錄", "記錄人對明確內容與範圍的核可"),
    "BL": ("Baseline", "案例基線", "凍結已核可的案例版本"),
    "RUN": ("Run", "測試執行紀錄", "保存某次實際執行的觀察與證據"),
}
ROUNDS = ["traceability", "executable", "coverage", "consistency"]
GROUPS = ["sources", "decisions", "questions", "requirements", "acceptance", "risks", "scenarios"]
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
        rows = reg.get(group)
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
        if source.get("kind") not in ("normative", "harness", "observation"):
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
                if rule.get("status") == "confirmed":
                    if not parents or any(p.get("status") != "confirmed" for p in parents):
                        error(f"{rid}: confirmed AC needs confirmed parent requirement")
                    require(rule, ["oracle"], rid)
                    require(rule.get("oracle", {}), ["observe", "when", "tolerance"], rid)
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
        if scenario.get("selection") not in ("keep", "merge", "defer", "clarify"):
            error(f"{sid}: invalid selection")
        if scenario.get("selection") == "merge":
            targets = refs([scenario.get("merged_into")], "scenarios", sid)
            if not targets or targets[0].get("selection") != "keep":
                error(f"{sid}: merged_into must target a retained scenario")
    scope = reg.get("scope", {})
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
        if not assertions:
            error(f"{cid}: no product assertion with rule basis")
        if set(case.get("ac_ids", [])) - asserted_ac:
            error(f"{cid}: claimed AC coverage lacks an assertion")
        require(case.get("verdict_rules", {}), ["pass", "fail", "inconclusive"], cid)
        if case.get("type") == "automated":
            require(case.get("automation", {}), ["command", "binding_refs"], cid + ".automation")
    if gate == "baseline":
        require(scope, ["objective", "in", "out", "selected_ac_ids", "selected_case_ids", "decision_ref"], "scope")
        refs([scope.get("decision_ref")], "decisions", "scope")
        if stale:
            error("Sources changed/missing: " + ", ".join(sorted(stale)))
        active_ids = set(selected + scope.get("selected_ac_ids", []) + scope.get("selected_risk_ids", [])
                         + scope.get("selected_scenario_ids", []))
        # Blockers on parent requirements, decisions or source documents also affect selected cases.
        for cid in selected:
            case = cases.get(cid, {})
            for key in ("ac_ids", "risk_ids", "scenario_ids"):
                active_ids.update(case.get(key, []))
            active_ids.update(case.get("environment", {}).get("binding_refs", []))
        pending = list(active_ids)
        flat = {rid: row for group in maps.values() for rid, row in group.items()}
        while pending:
            row = flat.get(pending.pop(), {})
            for key in ("requirement_ids", "source_refs", "decision_refs", "ac_ids", "risk_ids"):
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
    reg = {"schema_version": 1, "project": {"name": args.name or root.name, "owner": "unassigned"},
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
    doc = ["# 測試案例設計", "", "由 cases/*.json 產生。Actual 與執行判定另存 runs；本檔不是執行報告。", ""]
    for cid, case in cases.items():
        doc += [f"## {cid} — {case.get('title', '')}", "", f"狀態：{case.get('status')}；revision：{case.get('revision')}", ""]
        for key in ("purpose", "ac_ids", "risk_ids", "scenario_ids", "environment", "preconditions", "data"):
            doc += [f"**{key}**", "", "```json", json.dumps(case.get(key), ensure_ascii=False, indent=2), "```", ""]
        doc += ["| 步驟 | 操作／輸入 | 觀測／時機 | Expected／依據 | 證據 |", "|---|---|---|---|---|"]
        for step in case.get("steps", []):
            expected = "; ".join(f"{c.get('expected')} [{', '.join(c.get('rule_refs', []))}]" for c in step.get("checks", []))
            doc.append(f"| {step.get('n')} | {cell(str(step.get('action')) + ' / ' + str(step.get('input')))} | {cell(str(step.get('observe')) + ' / ' + str(step.get('when')))} | {cell(expected)} | {cell(step.get('evidence'))} |")
        for key in ("cleanup", "independence", "verdict_rules", "blockers", "automation"):
            doc += ["", f"**{key}**", "", "```json", json.dumps(case.get(key), ensure_ascii=False, indent=2), "```"]
        doc += [""]
    save_view("qa/test-cases.md", doc)
    catalog = ["# 專案編號字典", "", "由工具預設慣例與 registry.project.id_glossary 產生；修改來源字典後重新 render。", ""]
    catalog += legend(set(ID_TERMS) | set(overrides) | seen)
    safe(root, "qa/id-glossary.md").write_text("\n".join(catalog) + "\n", encoding="utf-8")


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
    # Deliberately do not carry implementation, observations or generation dialogue into reviewer context.
    permitted = {s["id"] for s in reg["sources"] if s.get("kind") in ("normative", "harness")}
    filtered = json.loads(json.dumps(data))
    filtered["registry"]["sources"] = [s for s in reg["sources"] if s["id"] in permitted]
    packet = {"artifact_digest": digest(data), "created_at": now(), "review_input": filtered,
              "instruction": "Reload cited normative and harness sources. Do not infer Expected from code or observed product behavior."}
    write(pack / "packet.json", packet, exclusive=True)
    (pack / "PROMPT.md").write_text(
        "請在新工作階段依 packet.json 審查測試案例。重讀已確認規格、選定範圍、操作介面依據及審查準則。\n"
        "分四輪：traceability、executable、coverage、consistency。逐輪列 Finding：ID、case_ids、rule_refs、issue、evidence、proposal。\n"
        "缺少產品規則則列待釐清，不得新增 Expected。不得從程式碼、產碼對話、目前 UI 行為推導 Expected。\n"
        "只處理選定範圍；記錄 reviewer、session、model（不知則 unknown）、at、independence 與 artifact_digest。\n"
        "自查須標記 same-session。尚未執行產品測試，不可填 Actual 或 Pass。將 review 放在 qa/reviews/<新 ID>.json，交人確認 findings。\n",
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
