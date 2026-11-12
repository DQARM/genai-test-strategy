# 結構化記錄契約

## 索引

1. 共同規則
2. Registry
3. 完整案例
4. 審查／核可
5. 執行記錄

## 共同規則

使用 UTF-8 JSON，沒有註解。所有路徑相對專案根目錄，禁止跨出根目錄與 symlink。時間用 ISO 8601 並帶時區。ID 不重用，修改內容增加 revision；同一規則被替代時保留 supersedes。以已讀來源為依據，不以本契約範例作為使用者產品規格。

ID＝Identifier（識別碼）。向人展示編號時，依 identifiers.md 提供英文來源、中文意思、用途與後綴說明；JSON 的 id／參照欄位仍只放原 ID。

人工決策共同欄位：`{"by":"實際決策人或使用者","at":"2026-11-09T15:00:00+08:00","evidence_ref":"qa/decisions/DEC-001.md"}`。evidence_ref 須存在並記錄實際回答或正式文件的確認依據。by 不得假填人名；沒有真實核可保持 pending，不執行 baseline。這是稽核記錄，並非身分驗證或電子簽章。

## Registry

init 產生 `qa/registry.json`，保留以下欄位：

- `schema_version`: 1。
- `project.design_policy`: 新專案為 `coverage-items-v1`。舊版缺少時仍可 draft 檢查與 render；所有新基線須先補本輪覆蓋項目並採用這項政策，詳見 [test-design.md](test-design.md)。
- `project`: 至少 name、owner；依已知內容可加 purpose、product_type、users、sut、interfaces、environment、quality_goals、constraints、unknown_fields。這些是專案背景，未知值可留 null；不要先替新專案填入教材角色、功能或數值。本輪選取另外記在 scope，不需更動 schema_version。
  啟動進度可加 `folder_mode`（new／existing）及 `requirement_input: {known_spec_note, mode, original_locations, snapshot_paths}`。`known_spec_note` 是使用者對「有沒有已知規格」的原回答摘要，例如有文件、只有口頭規則或目前沒有已知規格；不代表規則已確認。mode 是 pending／documents／conversation，分別表示文件狀態尚待回答、有文件、使用者確認目前無文件而由訪談開始。沒有文件不等於沒有已知規則。位置與副本清單為陣列，只記實際內容，不把讀取失敗當無文件。這些欄位可逐步補充，舊專案不必為續作重填；init 不自動填寫，由代理在取得使用者答案後更新。
  `id_glossary` 可保存本專案的前綴字典：`{"前綴": {"english": "英文來源", "meaning": "中文意思", "purpose": "用途", "basis": "定義依據"}}`。未知定義保留 null 並待確認。此欄位不改變 ID 或 schema_version；變更內容仍會改變設計 digest。
- `scope`: objective、in、out（沒有排除就明寫）、selected_ac_ids、selected_risk_ids、selected_scenario_ids、selected_case_ids、decision_ref。只有選定項目作為本輪覆蓋分母；所有未選風險仍須有取捨與剩餘風險。
- `sources`: `{id, path, sha256, locator, kind, status, version, note}`。kind 是 normative／harness／observation／experience；status 是 confirmed／unconfirmed。normative 是應然規則；harness 是可驗證操作介面；observation 是現狀；experience 是缺陷歷史或經驗線索，後兩者不可直接作 Expected 的規則依據。locator 提供頁碼／段落。使用 hashlib 或 inventory 取得真實 sha256，不手編。
  可加 `title`（方便閱讀的名稱）及 `excerpt`（實際讀取的相關摘錄，須保留 locator）；均非必填，不能為了網頁完整而編造摘錄。報告顯示這些已登錄欄位，不自行解析或完整嵌入原始 PDF／Word。新增欄位仍會改變 registry 的設計 digest。
  案例另引用的操作指南、輸入資料檔、自動化腳本及其依賴鎖定檔也登錄為來源並記 hash；尚未驗證的輔助內容標 unconfirmed，不因自動產生就當作已驗證。未登錄的外部依賴變化不會被 digest 自動察覺，必須先補足版本綁定。
- `decisions`: `{id, statement, by, at, evidence_ref, affected_ids, supersedes?}`。決策原文／摘要寫在對應 Markdown；同一回答可直接支持多項規則，不用重問。
- `questions`: `{id, text, status, owner, due_or_trigger, impact_ids, blocks, decision_refs}`。status 是 open／resolved／deferred。owner 不知填 unassigned。blocks 可為 baseline、execution、release；impact_ids 可含 ALL 或具體 ID。resolved 必須有 DEC 依據；deferred 仍是未解問題。
- `requirements`: `{id, text, revision, status, source_refs, decision_refs, confirmation, supersedes?}`。status 是 proposed／confirmed／superseded。confirmed 必須有 confirmed normative source 或 DEC，並有真實 confirmation。
- `acceptance`: 同 requirement 欄位，增加 `requirement_ids` 及 `oracle: {observe, when, tolerance}`。每個 AC 是可判定的規則；父需求必須已確認。容差不適用寫明「不適用：離散值須完全相等」。AC 不得加入來源未支持的新限制。
  `oracle.kind` 可為 specified／derived／implicit；舊記錄未填時按 specified 處理。confirmed 的 derived／implicit 另需 AC 的真實 decision_refs，以及 oracle.applies_when、limitations；derived 再填 relation。`oracle.reference_refs` 可連到已登錄且確認版本／內容的比較產物，保存 hash；experience 清單不作比較產物，它也不取代規則／DEC。共用 AC 在適用條件不變時可由多案引用，不逐案例重問。詳見 [oracles-exploration.md](oracles-exploration.md)。
- `risks`: `{id, failure, impact, likelihood, uncertainty, priority, rationale, evidence_refs, disposition, owner, residual_risk}`。未知 likelihood／uncertainty 可寫「資料不足」並解釋；不可改成假概率。
- `scenarios`: `{id, description, category, ac_ids, risk_ids, selection, reason, merged_into?}`。selection 是 keep／merge／defer／clarify。merge 指向一個 keep；正式範圍只選 keep。
  可加 `origin`（specification／experience／mixed）與 `source_refs`，追蹤候選產生線索；舊記錄相容，不由線索推導 Expected。
- `coverage_items`: `{id, ac_ids, technique, description, selection, reason, risk_ids?, scenario_ids?, decision_refs?, residual_risk?}`。COV 取自 Coverage，中文為覆蓋項目；後綴為流水號。technique 使用 test-design.md 的記錄值。selection 為 keep／defer；defer 必須有 residual_risk，基線前須有真實 decision_refs。本輪 selected_ac_ids 關聯的全部保留項目，須由 selected_case_ids 的斷言承接；沒有保留項目的已選 AC 不能建立基線。規則未決仍記 Q，不偽造可判定項目。
- `charters`: 探索任務設計，EXP 取自 Exploration。欄位為 id、title、status（draft／ready／retired）、mission、scope、timebox_minutes、source_refs、binding_refs、ac_ids、question_ids、preconditions、actions、stop_conditions、cleanup。ready 需要正整數時間上限、已確認的操作來源，以及具體初態、操作／觀察／證據、停止及清理方式；actions 每項含 action、observe、evidence，前置及清理每項含 action、verify。ac_ids 可以為空；有引用則須已確認。觀察／發現另存 evidence，不寫入任務設計。模板及紀錄要求見 oracles-exploration.md。

coverage_items、charters 在舊 schema 1 檔案可省略，不必為續作先重建全部專案；它們若存在會納入設計 digest，變動須重審對應新版本。

尚未確認的通用 AC 模板（不代表已核可；依專案填好並取得真實依據後才改 confirmed）：

```json
{
  "id": "AC-001",
  "revision": 1,
  "text": "填入本專案的條件、操作與可觀測預期結果；目前仍是草稿。",
  "status": "proposed",
  "requirement_ids": ["REQ-001"],
  "source_refs": [],
  "decision_refs": [],
  "confirmation": null,
  "oracle": {"observe": null, "when": null, "tolerance": null}
}
```

上例的 REQ-001 必須在實際 registry 中存在才可引用；來源與決策 ID 只填已登錄的真實記錄。模板不能直接作為 ready 案例的判準。

## 完整案例

`qa/cases/TC-001.json` 的 id 必須等於檔名。欄位：

- id、title、revision、status（draft／blocked／ready／retired）、purpose。
- ac_ids、risk_ids、scenario_ids。每個宣稱覆蓋的 AC 都要有具體斷言，不可只掛 ID。
- coverage_ids：本案關聯的 COV ID；對應 AC 也須列於 ac_ids。ready 案例宣稱的每個 COV 都要有本案步驟斷言承接。舊案例可暫缺此欄位繼續編輯，新基線須補齊。
- level（unit／integration／system／acceptance）、type（manual／automated）。
- environment：target、build_binding、tools、binding_refs（SRC ID）。binding_refs 指向已確認的 harness 或 normative 來源，說明實際可用操作及觀測介面；不得用觀測到的產品結果替代應然規格。
- preconditions：物件陣列，每項 action、verify，必要時 evidence。寫出如何建立、如何確認。
- data：陣列，包含 name、value、unit、basis；不需要外加資料時寫明原因，不能留空掩蓋缺口。
- steps：陣列，n 連續從 1 起，action、input、observe、when、evidence、checks。`checks: [{expected, rule_refs: [AC ID]}]`。純注入／操作步驟 checks 可空；整個案例至少有一個產品斷言。每個斷言引用已確認且列於 ac_ids 的 AC。
  斷言可加 `coverage_ids: [COV ID]`，引用的項目須列於本案 coverage_ids，且其全部 ac_ids 須在該斷言的 rule_refs 中。COV 不能代替 AC；工具只能查引用，不能證明輸入確實位於該分區或轉移。
- cleanup：物件陣列，每項 action、verify。無清理需求也必須解釋其無狀態／隔離依據。
- independence：如何獨立重跑、不依賴其他 TC。
- verdict_rules：pass、fail、inconclusive。規則未定、量測失效、步驟無法完成時不能判 PASS。
- blockers：Q ID 陣列；ready 必須為空。
- automation：如 type=automated，填 command、binding_refs、dependencies、status（generated-not-run／verified-executed）。命令須對應真實存在腳本／工具；測試有執行證據才標 verified-executed。
- provenance：author、model（不知道寫 unknown）、context_refs、created_at。不要編模型版本。

設計檔禁止填 actual 或 result。所有完整欄位並不保證語意正確；四輪審查還要檢查執行可行性與規格支持。

## 審查／核可

審查由 genai-test-review 接手，只新增 review；以下為兩個 Skill 共用的資料契約，不需要另一套 registry。規格、案例、scope、session 及基線的修改由設計端處理。

`qa/reviews/REV-001.json`：

```json
{
  "id": "REV-001",
  "artifact_digest": "由 digest 命令取得",
  "reviewer": "真實審查者",
  "session": "可辨識的新工作階段或人員審查記錄",
  "model": "unknown",
  "at": "實際時間",
  "independence": "fresh-session",
  "rounds": ["traceability", "executable", "coverage", "consistency"],
  "findings": []
}
```

independence 僅可如實填 fresh-session、human、same-session；same-session 不滿足正式基線的獨立審查要求。rounds 只記真正完成的輪次，來源或範圍不足則保留未完成並在 limitations 說明。沒有 findings 僅在實際審查後使用，不能預設填入以通過檢查。

Finding 欄位：id、round、case_ids、rule_refs、issue、evidence、proposal、status（open／fixed／dismissed／accepted-risk）、disposition（by／at／evidence_ref／reason）。accepted-risk 另附 residual_risk。修正造成內容改變，須對新 digest 重審；不是把舊 finding 的狀態改 fixed 就代表已重審。

`qa/approvals/APP-001.json`：by、at、evidence_ref、artifact_digest、case_ids。這份記錄只在使用者明確核可本次內容後產生。若人在同一回覆已確認規則、選取範圍並核可案例，可一次記錄各項授權；但未做獨立審查不能假造審查證據。

`baseline` 將目前資料、審查與核可凍結於 `qa/baselines/BL-001.json`。同 ID 不可覆寫。先執行 check --gate baseline 可看阻塞項目。這是案例基線，不是產品放行。

## 執行記錄

`start-run` 建立 `qa/runs/RUN-001.json` 並凍結 case／registry／digest／Git 狀態。填實際執行人、started_at、finished_at，逐步填 actual、status、at、evidence。證據格式：`{"path":"qa/evidence/RUN-001-step2.log","sha256":"真實檔案 hash"}`。

狀態為 NOT_RUN／PASS／FAIL／BLOCKED／INCONCLUSIVE。只完成準備或沒有判準就不標 PASS。run PASS 必須所有步驟有證據且為 PASS；FAIL 要有失敗步驟；未測步驟保留 NOT_RUN。重新跑建立新 RUN ID，不覆寫前次 Actual。

工具不會替你執行 SUT。使用 check-run 檢查紀錄完整性，再人工檢查證據與結論是否相符。不可修改 case_snapshot 或 registry_snapshot 來讓舊結果符合新規格。
