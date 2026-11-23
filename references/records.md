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

人工決策共同欄位：`{"by":"實際決策人或使用者","at":"2026-11-09T15:00:00+08:00","evidence_ref":"qa/decisions/DEC-001.md"}`。evidence_ref 須存在並記錄實際回答或正式文件的確認依據。by 不得假填人名；沒有真實核可保持 pending，不執行 baseline。這是稽核記錄，並非身分驗證或電子簽章。歷史時間未知時先在 interactions 保存原話及未知時間，規則保留 proposed 與待補項；不要為通過檢查新增缺資料的 DEC、偽填 confirmed 或把登錄時間當原決策時間。既有不完整紀錄保留並揭露檢查限制。

## Registry

init 產生 `qa/registry.json`，保留以下欄位：

- `schema_version`: 1。
- `project.design_policy`: 新專案為 `coverage-items-v1`。舊版缺少時仍可 draft 檢查與 render；所有新基線須先補本輪覆蓋項目並採用這項政策，詳見 [test-design.md](test-design.md)。
- `project.method_policy`：新專案採 `design-choices-v1`。方法選用資料存於 `design_choices`，舊專案續作見 [migration.md](migration.md#資料相容性)。
- `project`: 至少 name、owner；依已知內容可加 purpose、product_type、users、sut、interfaces、environment、quality_goals、constraints、unknown_fields。這些是專案背景，未知值可留 null；不要先替新專案填入教材角色、功能或數值。本輪選取另外記在 scope，不需更動 schema_version。
  啟動進度可加 `folder_mode`（new／existing）及 `requirement_input: {known_spec_note, mode, original_locations, snapshot_paths}`。`known_spec_note` 是使用者對「有沒有已知規格」的原回答摘要，例如有文件、只有口頭規則或目前沒有已知規格；不代表規則已確認。mode 是 pending／documents／conversation，分別表示文件狀態尚待回答、有文件、使用者確認目前無文件而由訪談開始。沒有文件不等於沒有已知規則。位置與副本清單為陣列，只記實際內容，不把讀取失敗當無文件。這些欄位可逐步補充，舊專案不必為續作重填；init 不自動填寫，由代理在取得使用者答案後更新。
  `id_glossary` 可保存本專案的前綴字典：`{"前綴": {"english": "英文來源", "meaning": "中文意思", "purpose": "用途", "basis": "定義依據"}}`。未知定義保留 null 並待確認。此欄位不改變 ID 或 schema_version；變更內容仍會改變設計 digest。
- `project.risk_policy`：新專案為 `requirement-risk-v1`。`project.risk_criteria` 保存 severity／likelihood／priority 各自的等級定義、status（proposed／confirmed）、source_refs、decision_refs；unknown 是資料不足，不能作最低等級。完整契約與舊資料處理見 [risk-assessment.md](risk-assessment.md)。
- `scope`: objective、in、out（沒有排除就明寫）、selected_ac_ids、selected_risk_ids、selected_scenario_ids、selected_case_ids、decision_ref。只有選定項目作為本輪覆蓋分母；所有未選風險仍須有取捨與剩餘風險。
- `sources`: `{id, path, sha256, locator, kind, status, version, note}`。kind 是 normative／harness／observation／experience；status 是 confirmed／unconfirmed。normative 是應然規則；harness 是可驗證操作介面；observation 是現狀；experience 是缺陷歷史或經驗線索，後兩者不可直接作 Expected 的規則依據。locator 提供頁碼／段落。使用 hashlib 或 inventory 取得真實 sha256，不手編。
  支援選填 `readings`：逐次保存實際閱讀範圍、正文／索引深度、定位摘錄、未讀部分、限制及版本。以 `record-reading` 追加或更正，舊紀錄不覆寫；缺欄位是未留下閱讀紀錄，空陣列是未讀。契約與 `source_citations` 例子見 [source-reading.md](source-reading.md)。來源 confirmed 不表示已讀；`note`／舊 `excerpt` 不自動轉為閱讀證據。
  可加 `title`（方便閱讀的名稱）及 `excerpt`（實際讀取的相關摘錄，須保留 locator）；均非必填，不能為了網頁完整而編造摘錄。報告顯示這些已登錄欄位，不自行解析或完整嵌入原始 PDF／Word。新增欄位仍會改變 registry 的設計 digest。
  案例另引用的操作指南、輸入資料檔、自動化腳本及其依賴鎖定檔也登錄為來源並記 hash；尚未驗證的輔助內容標 unconfirmed，不因自動產生就當作已驗證。未登錄的外部依賴變化不會被 digest 自動察覺，必須先補足版本綁定。
- `decisions`: `{id, statement, by, at, evidence_ref, affected_ids, interaction_refs?, supersedes?}`。實際決策寫在對應 Markdown，interaction_refs 指回原始 QA（Question and Answer，問答紀錄；後綴為流水號）。同一回答可支持多項規則；原話與 AI 解讀分開，不以解讀冒充原話。
- `interactions`：選填陣列，保存 QA 的 question_text、options、answer_text、answer_status、capture、interpretation、question_id、related_ids、真實已知時間／回答者及更正鏈。完整契約、pending 完成與缺原文處理見 [interview-records.md](interview-records.md)。record-qa 不會自動建立決策、增加需求題數或核可。
- `project.source_reading_policy`：新專案採 `source-reading-v1`。在有 `source_refs`／`binding_refs`／`oracle.reference_refs`／資料 `basis` 的同一物件加 `source_citations`，每項為 `{source_id, reading_seq, finding_index}`，指向該來源某次閱讀的某則摘錄。ready 的引用鏈需要有效正文證據；新基線要求政策及已選範圍依據完整。歷史專案可先草擬／閱讀，移轉規則見 source-reading.md。
- `questions`: `{id, text, status, owner, due_or_trigger, impact_ids, blocks, decision_refs}`。status 是 open／resolved／deferred。owner 不知填 unassigned。blocks 可為 baseline、execution、release；impact_ids 可含 ALL 或具體 ID。resolved 必須有 DEC 依據；deferred 仍是未解問題。
  另可選填 category、urgency、analysis、suggested_owner、options、source_refs／source_citations，支援規格缺口排序與轉交。完整定義見 [spec-review.md](spec-review.md)；qa/questions.md 是衍生視圖，不是第二份主資料或已訪談紀錄。
- `requirements`: `{id, text, revision, status, source_refs, decision_refs, confirmation, supersedes?}`。status 是 proposed／confirmed／superseded。confirmed 必須有 confirmed normative source 或 DEC，並有真實 confirmation。
  需求另有 `risk_assessment: {status, requirement_revision, rationale, source_refs, decision_refs}`，status 為 unassessed／proposed／confirmed，與需求本身的 status 分開；缺欄位視為未評估。評估版次綁需求 revision，confirmed 需真實決策或已確認 normative 來源。未辨識風險仍須留下檢視範圍與理由，不能當成零風險。
- `acceptance`: 同 requirement 欄位，增加 `requirement_ids` 及 `oracle: {observe, when, tolerance}`。每個 AC 是可判定的規則；父需求必須已確認。容差不適用寫明「不適用：離散值須完全相等」。AC 不得加入來源未支持的新限制。
  `oracle.kind` 可為 specified／derived／implicit；舊記錄未填時按 specified 處理。confirmed 的 derived／implicit 另需 AC 的真實 decision_refs，以及 oracle.applies_when、limitations；derived 再填 relation。`oracle.reference_refs` 可連到已登錄且確認版本／內容的比較產物，保存 hash；experience 清單不作比較產物，它也不取代規則／DEC。共用 AC 在適用條件不變時可由多案引用，不逐案例重問。詳見 [oracles-exploration.md](oracles-exploration.md)。
- `risks`: `{id, requirement_ids, failure, impact, severity, severity_rationale, likelihood, likelihood_rationale, uncertainty, priority, rationale, source_refs, decision_refs, evidence_refs, disposition, disposition_reason, owner, residual_risk}`。requirement_ids 是需求的直接多對多關聯。三個評等用專案定義代碼或 unknown，各自附理由；priority 理由用 rationale。暫緩使用 disposition=defer，另記 disposition_reason、residual_risk 與真實 decision_refs。既有 evidence_refs 自由文字保留，新版可解析的來源／決策用 source_refs／decision_refs；未知不能改成假概率。舊欄位與移轉見 risk-assessment.md。
- `scenarios`: `{id, description, category, ac_ids, risk_ids, selection, reason, merged_into?}`。selection 是 keep／merge／defer／clarify。merge 指向一個 keep；正式範圍只選 keep。
  可加 `origin`（specification／experience／mixed）與 `source_refs`，追蹤候選產生線索；舊記錄相容，不由線索推導 Expected。
- `coverage_items`: `{id, ac_ids, technique, description, selection, reason, risk_ids?, scenario_ids?, decision_refs?, residual_risk?}`。COV 取自 Coverage，中文為覆蓋項目；後綴為流水號。technique 使用 test-design.md 的記錄值。selection 為 keep／defer；defer 必須有 residual_risk，基線前須有真實 decision_refs。本輪 selected_ac_ids 關聯的全部保留項目，須由 selected_case_ids 的斷言承接；沒有保留項目的已選 AC 不能建立基線。規則未決仍記 Q，不偽造可判定項目。
- `charters`: 探索任務設計，EXP 取自 Exploration。欄位為 id、title、status（draft／ready／retired）、mission、scope、timebox_minutes、source_refs、binding_refs、ac_ids、question_ids、preconditions、actions、stop_conditions、cleanup。ready 需要正整數時間上限、已確認的操作來源，以及具體初態、操作／觀察／證據、停止及清理方式；actions 每項含 action、observe、evidence，前置及清理每項含 action、verify。ac_ids 可以為空；有引用則須已確認。觀察／發現另存 evidence，不寫入任務設計。模板及紀錄要求見 oracles-exploration.md。

選用的 `project.technique_catalog` 可登錄專案自訂方法。每筆提供唯一 `key`（例如 `project-clock-comparison`）、`title`（專案慣用名稱）、`when_to_use`、`required_inputs`、`deliverable` 和 `limitations`，皆為具體文字。方法登錄描述通用操作與限制；每個測試目標仍需獨立填選用理由、覆蓋準則與驗收依據。DES 與 COV 引用相同的 key 後，報告即可依該名稱篩選案例。

DES 取自 Design，代表一筆方法選用紀錄，數字是本類流水號。`design_choices` 的每筆記錄使用下列欄位。選用的是一個目標下的某種方法，同一目標可有多筆。

| 欄位 | 內容 |
|---|---|
| `id`、`objective`、`ac_ids` | 穩定編號、具體可驗證的目標、相應驗收條件。可用 `risk_ids`、`question_ids`、`decision_refs` 引用已登錄的風險、問題、取捨。 |
| `natures`、`quality_aspects` | 各填至少一項。前者取 `functional` 或 `non-functional`，兩者可並列；後者填專案品質面向，如「功能正確性」「效能效率」。案例的 `type` 仍專指人工／自動執行。 |
| `levels`（選填） | 列出這個選案決定適用的目標層級，使用下方案例 `level` 的代碼。提供時至少一個且不可重複。若不同層級的模型、品質面向或取捨不同，分筆記錄。缺省表示尚未指定層級。 |
| `technique`、`applicability` | 方法代碼見 [test-design.md](test-design.md)。適用性填 `applicable`、`not-applicable` 或 `unknown`。 |
| `measurement_profile`（量測方法選填） | 效能選案的可追溯摘要。填寫 `subtype`、`trigger`、`workload`、`metric`、`acceptance_basis` 五個字串，其餘方法沿用原欄位。 |
| `selection`、`reason` | 適用的方法可 `adopt`（採用）、`defer`（暫緩）、`exclude`（不納入）或 `pending`（待決）；不適用填 exclude；適用性未知填 pending 或 defer。說明選擇與適用性的理由，暫緩另填 `residual_risk`。 |
| `criterion`、`model_rows` | 採用時須連 AC、寫覆蓋準則與模型。每列有文字 `label`、`inputs`、`expected` 及陣列 `coverage_ids`。僅採用的方法可連 COV；該 COV 的方法須相同，所有 AC 均在本筆 `ac_ids` 中。尚未確定預期的列填空字串及空陣列，並指出缺哪項決策。 |

採用且涉及已選 AC 或風險時，未決列須以列上的 `question_ids` 或該 DES 的 `question_ids` 指到尚未結案的問題，依問題的 `blocks` 處理。已評為適用卻暫緩的本輪方法須在基線前連到真實取捨的 `decision_refs`，可共用既有決策。

效能選案的 `subtype` 可用 `load`、`stress`、`endurance`、`scalability`、`capacity`、`spike`、`concurrency`、`measurement`。依 [test-design.md](test-design.md) 選擇。`trigger` 記下引發量測的承諾或風險，沿用 DES 上的 AC 或風險引用。`workload` 描述已知負載與仍待釐清的條件，`metric` 記錄量測指標，`acceptance_basis` 指出適用條款或已確認 AC 與判定依據。若欠缺足以判定的依據，填空字串，模型列的 `expected` 填空字串、`coverage_ids` 填空陣列。本輪 `pending` 或 `adopt` 的未決依據在 DES 或模型列連到開放或延後的 Q（Question，待釐清問題）。可另外以探索任務收集觀察。有各自判準的工作負載或不同子類可分筆選用。同一子類在多個條件下驗證時，於模型分列負載與對應的預期。

例如已確認「整數設定 1 至 50 均可儲存」時，模型的上限列可寫成 `{"label":"上限值","inputs":"設定 50 並儲存，再重新讀取","expected":"讀得 50","coverage_ids":["COV-02"]}`。此列只承接上限值；對超出範圍的處置另查已確認規則。人閱讀的版本應能從模型列經 COV 到實際步驟斷言。

`design_choices`、`coverage_items` 與 `charters` 在舊 schema 1 檔案可省略。新增或修改這些記錄會改變設計 digest。

工具的風險可加 origin、affected_areas、assessment_status、question_ids，明列整合／變更／環境等非需求來源；缺省仍沿用原直接需求關聯，不自動豁免孤立風險，見 [risk-assessment.md](risk-assessment.md#不強迫所有風險源自需求)。覆蓋方法另支援 combinatorial、error-guessing、data-lifecycle，契約及判準要求不變。

選填排程資料放 qa/execution-profile.json，選取建議放 qa/selections/SEL-*.json；不納入設計 digest，但綁定各自指紋並可 check-selection。不得將現有設計欄位移出以規避審查；格式及命令見 [execution-selection.md](execution-selection.md)。

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

## 逐條比對契約與實作

若要保存規格與某版實作的比對，可在 registry 的 `contract_assessments` 陣列登錄。CMP 取自 Comparison（條款比對），數字為本類流水號。依據判讀與狀態範例見[驗證範圍與證據](evidence-scope.md)。

| 欄位 | 用途 |
|---|---|
| `id`、`clause`、`status` | 一筆對應一項可驗證承諾。狀態取 `not-assessed`（未判定）、`blocked`（受阻）、`conflict`（規格衝突）、`match`（觀察符合）、`gap`（實作落差）。 |
| `requirement_ids`、`ac_ids`、`contract_ref`、`derived_refs` | 可直接關聯原始需求，並列驗收條件、核定契約原件及由該原件衍生的文件或測試來源。若正式採納的原件就是 OpenAPI，可直接引用該檔。 |
| `target_build`、`environment`、`scope_basis`、`observed` | 目標版本、部署環境、支持這項判讀的理由與實際觀察。受阻及規格衝突需說明原因，可用 `question_ids` 連到待釐清事項。 |
| `observation_refs`、`source_citations` | 引用當版、同環境的直接觀測及讀取定位。對 `match`／`gap`，登錄已確認的規則與版本化契約。每個觀測來源的 `observed_build`、`observed_environment` 須與本筆相符，並依既有來源閱讀格式引用原件與觀測。 |

搜尋不到文件、測試台中斷或從同一契約生成的測試通過，都要依實際證據限定結論。事後有新的版本或觀察時另留紀錄；規則本身如需改動，沿用既有決策及修訂流程。新增或修改登錄內容會改變目前設計版本指紋。

## 完整案例

`qa/cases/TC-001.json` 的 id 必須等於檔名。欄位：

- id、title、revision、status（draft／blocked／ready／retired）、purpose。
- ac_ids、risk_ids、scenario_ids。每個宣稱覆蓋的 AC 都要有具體斷言，不可只掛 ID。
- coverage_ids：本案關聯的 COV ID；對應 AC 也須列於 ac_ids。ready 案例宣稱的每個 COV 都要有本案步驟斷言承接。舊案例可暫缺此欄位繼續編輯，新基線須補齊。
- `level` 的值為 `unit`（元件／單元）、`component-integration`（元件整合）、`system`（系統）、`system-integration`（系統整合）、`acceptance`（驗收），或 `integration`（整合範圍未細分）。`type` 為 `manual` 或 `automated`。
- environment：target、build_binding、tools、binding_refs（SRC ID）。binding_refs 指向已確認的 harness 或 normative 來源，說明實際可用操作及觀測介面；不得用觀測到的產品結果替代應然規格。
- 只有在對端會影響判定時，才在 environment 增列 `required_dependencies`。例：`[{"key":"radio","target":"RU-A / FW 2.3","mode":"real"}]`。`key` 在個案內唯一，`target` 表示能辨認的對端與適用版本；`mode` 可用 `real`（真實）、`simulated`（模擬）或 `either`（兩者都適用）。同一流程有可用模擬器驗證的本端行為，以及僅能用真機驗收的互通承諾時，可拆成兩個案例，各自保留可判讀的結果。
- preconditions：物件陣列，每項 action、verify，必要時 evidence。寫出如何建立、如何確認。
- data：陣列，包含 name、value、unit、basis；ready 案例每列須有名稱、單位、依據與明列的值，無量綱可寫「1」。數值 0 與布林值 false 都是有效輸入。若刻意傳空字串、null 或其他空值，保留該 value 並填 value_reason 說明測試目的。無需外加資料時可用單列 `[{"reason":"按鈕直接讀取裝置目前狀態"}]` 說明原因。
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
  "checked_case_ids": ["TC-001"],
  "rounds": ["traceability", "executable", "coverage", "consistency"],
  "findings": []
}
```

independence 僅可如實填 fresh-session、human、same-session；same-session 不滿足正式基線的獨立審查要求。rounds 只記真正完成的輪次，來源或範圍不足則保留未完成並在 limitations 說明。新基線逐一核對本輪選定案例是否各有四輪獨立審查。每份紀錄的 rounds 適用於該份明列的全部 checked_case_ids，檢查範圍不同時分筆保存。同一版可合計多份紀錄。既有審查缺少案例清單時保留原檔，待補足實際涵蓋證據才可用於新基線。沒有 findings 僅在實際審查後使用，不能預設填入以通過檢查。

交接另保留 `input_mode`（review-pack／direct-project）、`review_pack_id`（直接審專案填 null）、`review_input_digest`（包內過濾輸入的 hash，不能代替 artifact_digest）、`checked_case_ids`、`read_sources`（source_id／path、sha256、locator、read_scope、limitations）、`review_focus_checked` 及 `limitations`。舊結果可讀，不補造過往閱讀紀錄；新增審查依實際情形填。可攜包的 REVIEW_TEMPLATE.json 是空白結構，不能直接存進 reviews 冒充已審。僅驗證包時不能宣稱重算原專案完整 digest；審查結果須保留此限制。

Finding 欄位：id、round、case_ids、rule_refs、issue、evidence、proposal、status（open／fixed／dismissed／accepted-risk）、disposition（by／at／evidence_ref／reason）。accepted-risk 另附 residual_risk。修正造成內容改變，須對新 digest 重審；不是把舊 finding 的狀態改 fixed 就代表已重審。

`qa/approvals/APP-001.json`：by、at、evidence_ref、artifact_digest、case_ids。這份記錄只在使用者明確核可本次內容後產生。若人在同一回覆已確認規則、選取範圍並核可案例，可一次記錄各項授權；但未做獨立審查不能假造審查證據。

`baseline` 將目前資料、審查與核可凍結於 `qa/baselines/BL-001.json`。同 ID 不可覆寫。先執行 check --gate baseline 可看阻塞項目。這是案例基線，不是產品放行。

## 執行記錄

`start-run` 建立 `qa/runs/RUN-001.json` 並凍結 case／registry／digest／Git 狀態。填實際執行人、started_at、finished_at，由 record-run 逐步登錄 actual、status、at、evidence，避免手改整份凍結快照。證據格式：`{"path":"qa/evidence/RUN-001-step2.log","sha256":"真實檔案 hash"}`。

狀態為 NOT_RUN／PASS／FAIL／BLOCKED／INCONCLUSIVE。只完成準備或沒有判準就不標 PASS。run PASS 必須所有步驟有證據且為 PASS；FAIL 要有失敗步驟；未測步驟保留 NOT_RUN。重新跑建立新 RUN ID，不覆寫前次 Actual。

工具不會替你執行 SUT。使用 check-run 檢查紀錄完整性，再人工檢查證據與結論是否相符。不可修改 case_snapshot 或 registry_snapshot 來讓舊結果符合新規格。

### 使用 record-run

先將小型輸入 JSON 保存於專案內，例如 qa/run-input.json，再執行：

```bash
python3 qa/tools/qa_project.py record-run . --id RUN-001 --input qa/run-input.json
```

輸入示例是格式示意；操作人、Actual、時間、路徑及判定必須換成真實資料，不能直接當實測：

```json
{
  "operator": "實際執行人",
  "expected_revision": 0,
  "started_at": "2026-11-14T10:00:00+08:00",
  "steps": [{
    "n": 1, "status": "PASS", "actual": "實際觀察內容及判定依據",
    "at": "2026-11-14T10:00:01+08:00",
    "evidence": ["qa/evidence/RUN-001-step1.log"]
  }],
  "finish": true,
  "finished_at": "2026-11-14T10:00:03+08:00"
}
```

- 步驟 n 必須存在且不重複；只接受登錄欄位，不能傳入或改動 snapshot／digest／案例步驟。PASS／FAIL 要有現存證據，工具自算 SHA-256；不從檔案存在、hash 相符或關鍵字推論產品成功。
- 當次用到的對端可在 record-run 輸入頂層給出 `actual_dependencies`。例：`[{"key":"radio","target":"RU-A / FW 2.3","mode":"real","evidence_paths":["qa/evidence/peer-identity.log"]}]`。位置填實際佐證檔；工具在執行紀錄中存為 `evidence`（路徑與指紋）。混合環境逐項登錄。模式可用 `real`、`simulated`、`unknown`。省略會沿用同次執行已登錄的觀察，提供陣列則取代該次完整清單；更正已有對端時附原因。改換設備重跑另開執行紀錄。
- 對含對端要求的案例，結束時核對凍結版本內的目標、模式及當次證據。若基本彙總為 PASS／FAIL，但對端條件不足，整案為 INCONCLUSIVE，個別步驟的原始判讀保留。以舊版、模擬模式或其他次執行的資料支持本次指定實體對端均不足。
- 預設 finish=false，只存觀察。recording_status=in-progress，頂層 status 暫留 NOT_RUN（相容舊狀態列舉），報告顯示「登錄中；尚無最終結果」，不可當完全未測或正式通過。recording_policy=record-run-v1 為選填契約，不改 schema 1。
- 明確 finish=true 才彙總：存在 FAIL 優先，其次 BLOCKED、INCONCLUSIVE；所有步驟 PASS 且原案例 ready 才可 PASS。尚有 NOT_RUN 則不能 PASS，提前結束須 reason；僅剩 PASS 與 NOT_RUN 時結果為 INCONCLUSIVE。BLOCKED 指環境／操作阻塞，不能掩蓋已觀測的產品 FAIL。
- 實際 started_at、finished_at 及有結果步驟的 at 用含時區 ISO 8601；步驟須位於執行區間。缺實際步驟時間時用 at=null 與 time_unknown_reason 保存未完成觀察，不能 finish；不要用 now 補造。recording_events.recorded_at 才是工具自動產生的登錄時間。
- expected_revision 是選填的併發檢查值，取上一回覆的 recording_revision（初始為 0）。每次成功登錄自增、追加 recording_events，保留變更前後的結果及人員／理由；工具回覆只列精簡摘要。既有快照及設計 digest 不變。
- 覆寫已記步驟、修改已有時間／執行人或更正已結束紀錄，必須提供 reason，舊觀察保留於事件鏈。這僅供登錄更正，真正重跑一定建新 RUN。更正後未明確 finish 時回到未完成狀態。
- 寫入前檢查快照、證據、欄位及時間，再原子替換；無效輸入不保存。偵測到另一寫入者／版本衝突時停止並保留原檔。遺留 .lock 先查有無作業中程序，不自動刪鎖。
- 舊 RUN 沒有 recording_* 欄位仍沿用原 check-run 規則；不回填歷史。新工具不是身分驗證或防惡意竄改簽章，檔案、事件及判定仍需查核。


## 分析附表與相容性

品質面向的整體檢視放 strategy.md，方法及模型列存於 design_choices，實測回顧及可選度量放 plan.md。假想缺陷檢查寫在既有審查 finding.evidence／proposal，無法評估寫 limitations。舊包保留，新準則需升級專案工具後建立新包。
