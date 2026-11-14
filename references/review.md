# 審查交接、修正與核可

此文件供 genai-test-strategy 準備及接回審查。兩個 Skill 共用同一專案及資料契約，審查端只新增審查紀錄，設計端負責規格／案例修正及核可基線。工具的交接包自帶四輪準則，另一模型不需安裝 Skill 也能接手。

## 設計端交出待審版本

1. 完成本輪能交付的案例與結構檢查，保留已選範圍、必要依賴及仍受阻內容；不為方便審查移除範圍或未決事項。
2. 有特殊審查重點時先保存為 `qa/review-focus.md`；不只留在對話。執行下列命令，工具會沿用流水號、自動建立或重用有效包，驗證後才更新 `qa/review-handoff.json` 指向實際包。
3. 讀回命令結果及 `handoff_path` 指向的 HANDOFF.md，檢查 status／limitations；提供實際交接指令與位置。不能把準備命令、模板或已存在的審查結果當成已建立的輸入包。失敗時先修復可修復問題，無法完成就明列缺口，不假造路徑。
4. 一般同工作區用 reference 包；換模型／平台或原資料夾不可讀時用 portable 包，並提供真正 ZIP／資料夾。原始規格、操作文件、決策及閱讀證據依清單複製；不遞迴複製整個專案。排除無關產碼／生成對話；使用者選定且已登錄的來源仍可能含敏感內容，分享前依專案授權範圍檢視清單。
5. 記錄待審狀態與版本並 checkpoint；交接後不假稱接手者已讀或完成審查。

```bash
python3 qa/tools/qa_project.py prepare-review .
# 換模型／平台時改用：
python3 qa/tools/qa_project.py prepare-review . --portable
```

可用 `--focus-file <專案相對檔案>` 指定額外重點。舊 `review-pack --id <新編號>` 仍保留給明確指定包名的情況，也支援 `--portable`；一般使用 prepare-review 不必自己猜編號。REV 取自 Review（審查），數字是流水號；包在 review-packs、審查結果在 reviews，兩者不同。自動配號會避開兩處既有名稱，不改已有編號。

| 包內檔案 | 用途 |
| --- | --- |
| packet.json | 完整已選範圍、案例、結構化規則、相關原始問答、更正鏈、來源引用、版本與 review_focus |
| manifest.json | 每個包內檔案 hash、原始路徑與副本對應、available／missing／changed／excluded 狀態 |
| PROMPT.md、HANDOFF.md | 接手入口與實際交接位置；HANDOFF 另外說明跨平台提供方式 |
| REVIEW_GUIDE.md | 不依賴安裝 Skill 的四輪完整準則、獨立性與回傳要求 |
| REVIEW_TEMPLATE.json | 空白審查格式；rounds 空白、reviewer／independence 未填，不能當完成紀錄 |
| verify_pack.py | 只需 Python 標準函式庫的包驗證器 |
| payload/ | portable 才有；明列來源及證據的副本，原名由 manifest 對照 |

進入已解壓的 portable 包，執行 `python3 verify_pack.py check-review-pack .`；reference 包另加 `--project <原專案根目錄>`。提供 --project 會同時核對目前完整設計版本及原始來源。Windows 可用 `py -3`。沒有 Python 時可人工讀取，但須明列未做工具驗證的限制。verified-with-gaps 代表包完整性已檢查、設計或來源仍有缺口；不表示案例完整或產品通過。指紋只能檢查內容一致，不能證明真實性、已讀或理解。

## 審查端找包與換模型

- 只指定目前專案：用唯讀 `resolve-review <root>` 自動找目前版本且重點相符的有效包；沒有就用 direct-project 審目前資料，回報實際來源、版本與缺少特殊提示等限制，不假稱讀過包、不重新 init。
- 指定包或歷史 digest：用 `resolve-review <root> --pack <實際包 ID>` 或 `--artifact-digest <完整值>`。找不到、損毀或必要依據不可讀時列阻塞，不悄悄改用目前版本。可攜歷史包核對副本；reference 歷史包需要原對應版本文件。
- 舊協定 1／無 manifest 包可依原欄位人工核對；不能宣稱新式完整性驗證已通過。工具過舊時設計端保留版本後升級，審查端不擅自替換專案工具。
- 換模型時開新的對話，提供同一份實際 portable ZIP 或已解壓內容，請依 PROMPT.md 開始。平台不能解壓、讀圖片／附件時，明列限制並提供可讀的對應原檔；只有貼原機器路徑不能保證另一模型能讀。
- 新模型用 REVIEW_TEMPLATE 建立新的結果 JSON，回傳結果與摘要；沒有專案寫入權時直接交回，不要求先建專案或裝 Skill。保存實際 model／session、checked_case_ids、read_sources、review_focus_checked、完成輪次及限制。不能把同對話換模型標為 fresh-session。

review-pack 帶 interview_evidence_ids 與相關原始問答／更正鏈；獨立審查須核對人的回答是否支持決策中的適用條件，AI 解讀不是原話。未保留原文則列限制，不把歷史摘要補成逐字稿。

review-pack 保留來源 readings、source_citations 與 source_reading_summary。交接須提供相關原檔及閱讀證據檔；審查逐一回到引用的版本、正文／圖表及上下文，查摘錄是否忠實且支持規則。不能只因引用存在或標為 scoped 就通過。僅目錄、缺頁、錯誤解讀、過期或已更正摘錄均列具體 Finding；審查端不改來源紀錄，由設計端追加閱讀／修正後以新 digest 重審。

## 獨立性與版本

只有真實新工作階段重新載入依據才標 fresh-session；原對話自查標 same-session，人實際審查才標 human。換模型可降低部分共同偏誤但不保證獨立判準；同源假設即使在程式與案例中一致，仍需查明規格支持。沒有獲准或環境不支援時不自行建立代理，改交新對話包。

審查版本以完整設計 artifact_digest 為準；packet 的 review_input 可能過濾來源種類，不能對該子集另算 digest 冒充原始完整版本。來源 hash 也須與實際文件相符。舊版審查只適用該版，來源不可讀或未檢完全部範圍時，對應輪次不能列完成。

## 設計端接回發現

讀取實際 review 檔的版本、review_pack_id、完成輪次、limitations 與 findings；核對 review_input_digest 與包一致，以及原設計是否已變。不要只看「通過」文字。接回前重新查 REV／F 編號是否已佔用；有碰撞時使用新編號並另記原返回編號的對應，不覆寫歷史或改原返回檔。過期結果仍保存到其原版本，不能套用目前 digest。每項 Finding（發現）應有案例／規則、具體問題、證據及修正建議。依人的實際處置修正、合併、暫緩、待釐清、接受剩餘風險或有依據駁回，不能代填核可。

沿用原 session 的焦點、累計題數、本批額度、續問狀態與選擇依據。已確認答案不重問；只有本批仍可提問且確有必要時才釐清。等待選擇時先依原檢查點取得續問選擇，已選先產出或明訂總上限已到時只列待辦，不藉修正重新訪談。操作缺口先查文件或交合適負責人。

產品規則、範圍或案例一旦修改，更新 revision／supersedes、相關覆蓋項目、進度及閱讀網頁，再取得新 digest 交回重審。保留舊 review；記錄發現與修正的關聯，不改舊 digest。只改 Finding 為 fixed 不代表新內容已審查。

## 核可基線

正式基線需要目前完整設計的四輪獨立審查、發現已有人處置，以及人對目前內容的明確核可。使用者已明確核可相同內容時不重問；沒有實際核可不得代填。

新基線使用 coverage-items-v1：每個已選 AC（Acceptance Criterion，驗收條件）有保留 COV（取自 Coverage，覆蓋項目），全部保留項目有已選案例斷言；暫緩項目具有人決策與剩餘風險，同時保留 AC／風險／情境的檢查。舊專案依 test-design.md 補齊資料，新 digest 重審；舊基線與執行快照不改寫。

工具的新基線另依 [risk-assessment.md](risk-assessment.md) 採 requirement-risk-v1：本輪涉及需求的評估已確認、風險分級有依據、已選風險有案例，其他關聯風險有暫緩決策。全專案未選需求仍可未評估，不因此重啟訪談。

工具只能驗證結構，不能證明規格、覆蓋模型及自由文字正確。核可記錄與 baseline 由設計端依 [records.md](records.md#審查核可) 及 [local-versioning.md](local-versioning.md) 建立；案例基線不是產品放行。

工具的 risk_evidence_source_ids 保留風險初評引用的觀察資料；這些資料只支持危害／可能性分析，不能取代已確認的產品 Expected。未引用的任意現況觀察仍不加入審查包。
