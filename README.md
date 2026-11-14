# GenAI 測試策略 Skill 使用手冊與 SOP

| 項目 | 內容 |
|---|---|
| 手冊版本 | 1.23.0 |
| 更新日期 | 2026-11-13（Asia/Taipei） |
| 適用專案工具 | qa_project.py 1.10.0；實際執行前以 --version／--help 確認 |
| 設計入口 | genai-test-strategy |
| 審查入口 | genai-test-review |

用自己的需求草稿或口頭規則，釐清可驗證規格、找出優先風險，再產生能照做、能判定的 Test Case。適用軟體、系統、設備與手動測試；不需原始碼、測試框架或 CI/CD。GenAI 指用 AI 協助流程，被測產品不必使用 AI。

本手冊教你如何操作。AI 的完整流程集中於 [workflow.md](references/workflow.md)，欄位見 [templates.md](references/templates.md)，升級見 [migration.md](references/migration.md)，功能沿革見 [CHANGELOG.md](CHANGELOG.md)。教學範例只提供寫法，不會成為新專案的預設規格。

## 目錄

- [1. 開始一個專案](#1-開始一個專案)
- [2. 讀資料、釐清與選擇何時產出](#2-讀資料釐清與選擇何時產出)
- [3. 找出最值得測的風險](#3-找出最值得測的風險)
- [4. 產生完整案例](#4-產生完整案例)
- [5. 閱讀成果與問答紀錄](#5-閱讀成果與問答紀錄)
- [6. 換模型獨立審查](#6-換模型獨立審查)
- [7. 修正、核可與案例基線](#7-修正核可與案例基線)
- [8. 安排與執行手動測試](#8-安排與執行手動測試)
- [9. 保存、續作與變更](#9-保存續作與變更)
- [10. 版控、同步與備份](#10-版控同步與備份)
- [11. 命令列速查](#11-命令列速查)
- [12. 遇到問題時](#12-遇到問題時)

**編號怎麼讀：** ID 是 Identifier（識別碼）。下列前綴加流水號用來追蹤資料；數字不代表優先度、版本或通過。AI 每份回覆／文件首次展示前綴時也會說明含義。既有專案沿用原編號；完整規則見 [編號字典](references/identifiers.md)。

| 前綴 | 英文來源 | 用途 |
|---|---|---|
| SRC | Source | 資料來源 |
| REQ | Requirement | 需求 |
| AC | Acceptance Criterion | 驗收條件 |
| Q | Question | 待釐清問題 |
| QA | Question and Answer | 原始問答紀錄 |
| DEC | Decision | 已作出的決策 |
| RISK | Risk | 風險；這是完整單字 |
| SC | Scenario | 候選情境 |
| COV | Coverage | 具體覆蓋項目 |
| TC | Test Case | 測試案例 |
| EXP | Exploration | 探索任務 |
| REV／F | Review／Finding | 審查紀錄／審查發現 |
| APP／BL | Approval／Baseline | 人員核可／案例基線 |
| RUN／SEL | Run／Selection | 實際執行紀錄／執行選取建議 |

例如 REQ-01 是需求類別的第 01 號記錄。新增與更正會保留修訂關係，不因換對話重新編號。

## 1. 開始一個專案

在能讀寫專案的 AI 環境使用已安裝的 Skill。要保存本機版本，需要該執行環境具備 Python 3.10+ 與 Git；只在對話討論可以先不用建檔。

貼上：

```text
請使用 genai-test-strategy，協助我釐清需求並設計 Test Case。
```

AI 先確認有無規格，再讀本輪資料、理解要處理的流程；資料夾及版控延到第一次需要保存時，已給資訊不重問。

| 入口 | 使用方式與成果 |
|---|---|
| 先對話產出 | 說「先在對話釐清並產出草稿」；不建資料夾，清楚標示未保存，規則及操作不足仍列受阻 |
| 保存成專案 | 指定新建／現有資料夾，再選本機 Git 或 Git server；保留問答、規則、案例、追溯與報告 |

你不必先選完整模式。只想討論可以直接開始；要保存或續作時再接入專案。從對話轉成專案會沿用原回答、編號與進度，不重新訪談。審查、核可及執行按任務需要接續；實際執行時都需保存證據，不限於稽核用途。

例如專案可放 `D:\Projects\Product-A`，草稿在另一個資料夾。這只是示例路徑，AI 必須能實際存取；雲端環境不能直接讀你的 Windows 磁碟。可改提供附件、掛載位置，或先選對話草稿。

外部來源保留原檔，將本輪需要的副本收進專案，記原位置與版本。遠端已有內容時先接手工作副本，再初始化；原資料夾已初始化就直接續作。只選本機時不需 Git server 帳號或網路。

## 2. 讀資料、釐清與選擇何時產出

有草稿時，先讓 AI 讀原文並分析缺口；無文件時從已知口頭規則開始。資料很多可先聚焦一個可交付流程，再擴大範圍。

```text
這次先處理「填入實際使用流程」。
請先閱讀相關來源，列出已讀章節、定位摘錄、重要缺口與可先完成的部分。
不要只根據檔名、目錄或來源登錄狀態判斷內容。
```

閱讀報告會分開列來源版本、實讀範圍、摘錄與未讀部分；「有 SRC」不等於「已讀」，「已讀」也不等於「已採納」。你可以從報告連回原檔與定位核對。

**訪談節奏：** 一次一題、每五題統整一次；仍需決策時，由你選「繼續釐清」或「先產出」。五題是統整頻率，預設沒有總題數上限，也不表示只剩五個問題。準備資料夾、版控及來源位置不計需求題數。你可隨時要求先產出；資料足夠時 AI 會提前整理。你明訂的總題數／時間限制優先，完整計數與續作規則見 [流程說明](references/workflow.md#本輪範圍與釐清預算)。

```text
先不要再問，請依目前已確認資料產出策略與案例草稿。
缺規則或操作的部分列具體缺口，其他部分繼續完成。
```

不知道可以直接回答「待確認」。AI 會保存影響、責任人或未指派、確認時點；不會用猜測填 Expected（預期結果）。選先產出也不代表你接受剩餘風險。

**PM 或工程不在場時：**

```text
請先分析這批草稿，整理歧義、衝突、邊界及可測試性缺口。
目前無法逐題回答，請匯出可轉交的規格問題單，再做可完成的案例草稿。
```

AI 以原 questions 記錄生成 `qa/questions.md`，包含來源定位、影響、排序、選項與空白填答。匯出不代表已訪談或已決策。先另存填答副本或在對話回覆，再讓 AI 接回原記錄；直接填寫生成檔可能被下次 render 覆蓋。

## 3. 找出最值得測的風險

```text
請依目前資料評估本輪需求的失敗情境及危害，指出最值得先測的項目。
分開說明危害嚴重度、發生可能性、測試優先序與依據；資料不足保留未知。
考慮手動測試、實機及取證成本，先提出少量有價值的候選情境。
```

每個需求保留未評估／已有初評／已確認狀態，風險可以多對多關聯；整合、變更、環境、架構、遺漏及團隊經驗也可成為風險來源，不需創造假需求。

AI 也會先篩選 [品質特性](references/quality-characteristics.md) 的適用性與理由；系統／設備另檢視符合性、互通、強健、長時間穩定性與時序。缺負載、時長或容差會列問題，不自行加上數值，也不逐欄追問你。

AI 會依失效機制選方法與深度，例如邊界、決策表、狀態／轉移對、組合或資料生命週期；記錄成本、選取理由及未測部分。嚴重度不直接等於優先序，unknown 不等於低風險。技術分析由 AI 完成，只把影響取捨的重要分歧交給你決定。

你或既有明確授權決定候選保留、合併、暫緩或待釐清。細節見 [風險評估](references/risk-assessment.md)、[失效機制](references/failure-modes.md) 與 [測試方法](references/test-design.md)。

## 4. 產生完整案例

```text
請依本輪選定範圍，先列目前已知條件、確認狀態、來源與缺口，再產生完整案例。
每筆都要有獨立前置、真實操作、資料、判定時機、觀測點、Expected 及其依據、證據與清理方式。
```

AI 先選方法、列具體 COV，再讓案例資料、初態及斷言承接。已知條件摘要是核對用，不需重新核可已確認內容；每批呈現一次，後續只列變動。

| 完整案例內容 | 你應能看懂什麼 |
|---|---|
| 目的與追溯 | 驗證哪個失敗情境，對應哪些 AC、風險、來源版本及 COV |
| 環境與版本 | 受測系統 SUT（System Under Test）的版本、工具、權限與實際操作介面 |
| 前置與資料 | 如何自行建立並確認初態，使用什麼值、單位與資料檔 |
| 編號步驟 | 到哪裡、做什麼、輸入什麼、何時看哪個輸出 |
| 判定與證據 | 每個 Expected 的已確認規則，以及要留下什麼證據 |
| 清理與重跑 | 如何恢復／隔離狀態，不依賴其他案例先成功 |
| 缺口 | 哪個規則、介面、環境或觀測能力仍不足 |

短批次可要求「用緊湊案例表呈現」：共通環境與前置集中列一次，每案保留獨立初態、編號步驟、Expected／依據、證據、清理與缺口。複雜案例仍展開；保存正式案例時補回各案完整欄位，不能依賴前一案例成功。

只有「測試登入」「確認正常」等標題還不是完整案例。真實 UI／CLI／API／設備介面未知時，AI 會列受阻，不自行命名按鈕或命令。介面成功、資料保存、下游完成及實機效果各有證據，不能互代。

| 設計狀態 | 含義 |
|---|---|
| draft | 草稿，仍在整理 |
| blocked | 有具體缺口阻止執行或判定 |
| ready | 設計具備所需條件；尚不等於已核可或已執行 |

共同判準可依已確認的適用條件重用；判準不足但操作已有依據時，可先設計有時間上限的探索任務，結果只作觀察。Actual（實際結果）留待實測另記。人工程序與自動化程序都適用。

可用的[完整模板](references/templates.md)、[跨領域指引](references/domain-adaptation.md)、[具體示例](references/worked-example.md)及[共用判準／探索](references/oracles-exploration.md)按需要閱讀。

## 5. 閱讀成果與問答紀錄

日常打開 `qa/report.html`，可點來源、規則與案例，雙向追查「這個案例參考哪些 SRC」「這份來源支撐哪些案例」。報告也顯示閱讀摘錄、問答、更正、風險、覆蓋與缺口。

「審查與基線」「實測紀錄」可從案例點入，查看各版本的審查發現、核可、凍結 Expected、Actual 與證據。歷史結果不套用到新設計；登錄中的觀察另標示，紀錄數量也不代表通過數。

| 檔案 | 用途 |
|---|---|
| qa/registry.json、qa/cases/ | 結構化主資料與完整案例 |
| qa/strategy.md、qa/plan.md | 測試策略與本輪安排 |
| qa/session.md | 目前進度、續問選擇、待辦及下一步 |
| qa/spec.md、qa/test-cases.md、qa/traceability.md | 規格、案例及追溯的生成視圖 |
| qa/source-reading.md、qa/interview.md、qa/questions.md | 閱讀依據、原始問答、規格問題單 |
| qa/risks.md、qa/test-design.md、qa/id-glossary.md | 風險、方法／覆蓋及編號說明 |
| qa/decisions/、qa/reviews/、qa/approvals/ | 決策、審查與核可 |
| qa/review-packs/、qa/baselines/ | 審查交接包與案例基線 |
| qa/runs/、qa/evidence/ | 實測紀錄與證據 |
| qa/execution-profile.json、qa/selections/ | 選填執行安排與選取建議 |

主資料變動後由 render 更新生成視圖，避免在報告另改一份規格。HTML 是離線檔案；分享時連同所引用的資料夾及合適的存取範圍，單傳 HTML 不會帶上全部原檔。細節見 [閱讀報告](references/report.md)。

```text
請顯示與這筆需求相關的原始提問、選項、我的回答及更正鏈。
把原話與 AI 解讀分開，指出決策與案例引用了哪些部分。
```

更正會新增紀錄並保留舊內容；有回答不代表每一項產品規則都已確認。完整欄位及操作見 [問答記錄](references/interview-records.md)。

## 6. 換模型獨立審查

案例交付時，設計端通常會準備並驗證交接包，提供實際 `HANDOFF.md` 位置。對話草稿、尚無案例或你要求暫不打包時會說明限制，不給不存在的包路徑。

**同工作區：** 開新對話，貼實際 HANDOFF 內容，讓 `genai-test-review` 讀指定版本。

**換模型或平台：**

```text
請準備可攜審查包，包含原始來源副本、特殊審查重點、四輪準則與回傳格式。
驗證後提供實際 ZIP，讓另一個模型在新對話獨立審查。
```

1. 取得實際產生的 ZIP。包包含 manifest、PROMPT、REVIEW_GUIDE、packet、來源副本與 REVIEW_TEMPLATE。
2. 在另一模型的新對話提供 ZIP／解壓內容，請它從 `PROMPT.md` 開始，依 `REVIEW_GUIDE.md` 審查，按 `REVIEW_TEMPLATE.json` 回傳。
3. 接手者依 manifest 的 bundle_path 讀副本，無須安裝另一個 Skill，也不需原機器路徑；無法驗證或閱讀的部分列限制。
4. 拿回結果，由設計端核對版本及編號碰撞，再依你的處置修正。

reference 包需要原專案；portable 包包含來源副本。`verified-with-gaps` 表示仍有缺口，不等於案例通過。包完整性驗證不代替內容閱讀，只有包時也不能宣稱重算原專案完整 digest（設計內容識別值）。

四輪是規格追溯、可執行／可判定、已選範圍覆蓋、一致性；可一次交付，不是四輪訪談。Finding 應列案例／規則、具體差異、證據與建議。審查端不改規則、案例或進度。

同對話換模型／Skill 仍是 same-session（同工作階段）；新工作階段重新閱讀指定依據才是 fresh-session；人實際審查才是 human。不同模型也可能有共同偏誤，最終核可仍由人決定。

只提供現有文件也可審查；未指定歷史包且無有效包時可直接審目前專案並列限制。明確指定的歷史包若缺失，會保留阻塞，不自行換版。詳見 [交接流程](references/review.md) 與 [審查 Skill](https://github.com/DQARM/genai-test-strategy/tree/dev/skills/genai-test-review)。

第三輪會檢查「若有合理的實作錯誤，哪個步驟的斷言能發現？」並記可辨識、缺口或無法評估；這是設計推演，沒有執行就不當抓錯實績。審查校準使用獨立測試資料，不往正式包埋瑕疵。

## 7. 修正、核可與案例基線

```text
請接回這份審查，列受影響的規則與案例，依我已確認的處置修正。
沿用原編號、進度與訪談選擇，修改後對新版本重新審查。
```

設計變更會更新 revision 與 digest。舊審查保留原版本，不改成新 digest 冒充已審。人員核可與正式案例基線是按需步驟，不是開始需求討論的條件。

建立基線時：

1. 固定本輪 registry、案例、策略、計畫及決策依據，核對選定範圍、未測部分與剩餘風險。
2. 完成目前完整設計版本的四輪獨立審查，處理 Finding；補足本輪風險、覆蓋與閱讀政策所需依據。
3. 人明確核可同一 digest 與確切案例清單，保存原話及 APP。
4. 建立新 BL 與 checkpoint，舊基線／標籤保留。

純案例核可的原話可放 `qa/approvals/APP-001-confirmation.md`，由核可 JSON 引用，避免純簽核又改到已審設計。核可同時要求改規則時，先改再審新版本。APP 的 case_ids 必須恰好等於選定案例清單。記錄格式與條件見 [records.md](references/records.md) 及 [review.md](references/review.md)。

案例基線代表接受這一版案例；產品放行另需實測證據與決策。

## 8. 安排與執行手動測試

只需要安排人工測試時，可以說：

```text
請依這次變更及 smoke 標籤提出回歸清單，列命中理由、優先序、估計時間與未覆蓋風險。
時間未知保留未知，受阻案例要看得見，不要因時間預算自動刪案。
```

選填 `execution-profile.json` 保存標籤、優先序及時間；select-cases 依已登錄變更關係與標籤取聯集。選取建議不改原 scope，也不代表已執行；執行前用 check-selection 核對版本，再看工具未登錄的依賴。詳見 [執行安排](references/execution-selection.md)。

要實測時再提供實際 SUT 版本、環境與授權操作，由人或工具照案例執行。start-run 只建立 NOT_RUN 與快照，不會操作產品，也不強制代辦全部基線／阻塞檢查。

使用 record-run 逐步記 Actual、實際時間、狀態、證據及執行人；完成時明確 finish，詳見 [實測登錄](references/records.md#執行記錄)。工具計算證據指紋、保留更正及凍結快照，不操作產品。未知執行時間保留未完成，登錄時間不冒充實測時間。完成 check-run 後仍要判讀證據。測試專案的 Git HEAD 不等於產品 build；無原始碼可用韌體／安裝包 hash 或供應商版本，未提交的產品差異另保存。

| 結果 | 使用條件 |
|---|---|
| NOT_RUN | 尚未執行 |
| PASS／FAIL | 前提及觀測有效，實測符合／不符合已確認 Expected |
| BLOCKED | 環境、權限、前置等阻止完成 |
| INCONCLUSIVE | 已有觀察，但判準／證據不足以可靠判定 |

放行報告列版本、已驗與未測範圍、阻塞／缺陷、證據及剩餘風險，由人明確決定。工具檢查通過、案例核可或所有案例 PASS 都不自動等於核准放行。

## 9. 保存、續作與變更

每題立即保存原始問答、真實決策與精簡進度；收尾集中更新完整案例、檢查、報告及版本。你若指定逐題提交／同步，AI 沿用該設定。

```text
請保存本次成果並更新 session，列出實際交付、重要缺口及下一個動作。
```

下次指定原專案即可：

```text
請使用 genai-test-strategy，接續「實際專案根目錄」。
先從 session 恢復進度，保留編號、有效決策與續問／先產出選擇。
```

案例產生後想再收集資料，可以明說：

```text
接續原專案，我要再釐清「實際流程或缺口」。
沿用原編號與記錄；收到新答案後，更新受影響規則、風險與案例，再安排重審。
```

來源或規則變更先讀差異，再追查受影響案例；現行案例標待更新／受阻，原基線和 RUN 不覆寫。舊結果只代表舊版本。

大型專案按目前焦點載入必要來源與共通限制，session 用連結定位完整記錄。這能減少部分重複輸入，但宿主可能仍帶入歷史；工具不提供 token 計量、費用硬限制或歷史裁切。題數不是 API 費用上限，沒有實際用量不宣稱節省比例。

## 10. 版控、同步與備份

本機 Git 可完全離線工作。checkpoint 預設保存 qa、專案標記、工具建立的 ignore 檔，以及明確登錄的來源／決策／閱讀證據；其他內容先檢查，再用 `--include` 明確加入。既有 staged 變更會保留並阻止混合提交。

選 server 後，AI 沿用服務、帳號、儲存庫、分支及上傳範圍；缺少登入才引導官方連線／授權介面，已登入且權限足夠就續用。密碼、驗證碼與安全金鑰在官方介面操作，不貼到對話。登入或同步暫時失敗仍可繼續本機工作，狀態保持待處理。

qa_project.py 自己不設定 remote 或 push；AI 另外同步並讀回。checkpoint 成功只代表本機保存。檔案快照上傳與完整 Git 分支歷史要分清；本 Skill 不替每位使用者指定 dev／main 分支政策。細節見 [Git server 指引](references/git-server.md)。

備份應涵蓋工作檔案、`.git` 歷史及必要證據。Git bundle 只含已提交歷史，不含未提交或被忽略檔案；`qa/evidence/raw/` 等大型證據另安排保存，hash 無法重建遺失原檔。本機歷史不等於異地備份。

復原先比較差異、輸出到新的比較檔，再依明確範圍套用；保留歷史與舊基線標籤。詳細命令及版本綁定見 [本機版控](references/local-versioning.md)。

## 11. 命令列速查

通常由 AI 操作。以下在實際專案根目錄執行；Windows 用 `py -3`，Linux／macOS 可用 `python3`。路徑含空白要加引號，示例 ID／路徑須換成實際值。

第一次從**技能包內**工具初始化，專案自帶工具尚未存在：

```powershell
py -3 "C:\Skills\genai-test-strategy\scripts\qa_project.py" init "D:\Projects\Product-A" --name "Product-A"
```

進入專案後：

```powershell
Set-Location "D:\Projects\Product-A"
py -3 qa/tools/qa_project.py --version
py -3 qa/tools/qa_project.py --help
py -3 qa/tools/qa_project.py inventory .
py -3 qa/tools/qa_project.py check .
py -3 qa/tools/qa_project.py render .
py -3 qa/tools/qa_project.py checkpoint . -m "保存本輪規格與案例"
```

| 命令 | 作用；詳細格式以子命令 --help 為準 |
|---|---|
| record-reading／show-source | 追加實讀定位／更正，或讀閱讀索引；不代替讀原檔 |
| record-qa／show-qa | 保存原始問答，或選讀原文；不自動確認產品規則或計數 |
| export-questions | 匯出問題單；不自行回答 |
| select-cases／check-selection | 提出執行建議／核對保存建議的版本 |
| digest | 列出整份設計內容識別值 |
| record-run | 以 --id、--input 追加觀察／有理由更正，明確 finish 才彙總結果；不重寫凍結設計 |
| prepare-review | 配號或重用已驗證交接包；--portable 另產生來源副本與 ZIP |
| resolve-review | 唯讀尋找適用包，缺包時說明直接審專案的限制 |
| check-review-pack | 驗證包指紋；--project 另核對目前專案完整設計 |
| review-pack | 明確指定新 ID 建包；保留既有包 |
| baseline | 核對條件及真實 approval，凍結案例版本 |
| start-run／check-run | 建立未執行快照／核對結果與證據結構 |

常用延伸操作：

```powershell
py -3 qa/tools/qa_project.py show-qa . --id QA-001
py -3 qa/tools/qa_project.py export-questions .
py -3 qa/tools/qa_project.py select-cases . --changed REQ-001 --tag smoke --budget-minutes 60
py -3 qa/tools/qa_project.py digest .
py -3 qa/tools/qa_project.py prepare-review . --portable
py -3 qa/tools/qa_project.py resolve-review .
```

prepare-review 會回報實際包、ZIP 及 HANDOFF 位置，不必猜包名。解壓後可用 `py -3 verify_pack.py check-review-pack .`；reference 包另加 `--project "可讀專案根目錄"`。

核可基線範例須先有目前版本的四輪獨立審查及真實 APP；執行範例須先核對環境、授權、基線與阻塞：

```powershell
py -3 qa/tools/qa_project.py check . --gate baseline
py -3 qa/tools/qa_project.py baseline . --id BL-001 --approval qa/approvals/APP-001.json
py -3 qa/tools/qa_project.py checkpoint . -m "核可案例基線" --tag qa-baseline-BL-001
py -3 qa/tools/qa_project.py start-run . --id RUN-001 --case TC-001 --sut-version "實際 build 或產物 hash" --environment "實際環境與工具版本"
```

真正執行並填結果後才用 `check-run . --id RUN-001`，保存實際證據。重跑用新 ID，避免覆寫快照。

查看版本與差異：

```powershell
git status --short
git log --oneline --decorate -10
git diff -- qa
git ls-files
```

輸入 JSON 範例與欄位分別見 [問答](references/interview-records.md)、[閱讀](references/source-reading.md)、[執行選取](references/execution-selection.md)及[資料契約](references/records.md)。

## 12. 遇到問題時

| 現象 | 下一步 |
|---|---|
| 路徑不可讀、找不到 Git／Python | 在 AI 實際執行環境確認存取與依賴；可先做對話草稿 |
| Not initialized／根目錄不符 | 找正確 Git 工作目錄；新專案才 init，不把 --standalone 當通用解法 |
| 已有非空 qa/ | 先辨識現有用途與資料，保留內容再安排遷移 |
| Existing staged changes preserved | 看 git diff --cached，先處理原有暫存範圍；不混入本次提交 |
| source missing or changed | 找回來源或讀新版差異，更新真正的引用與影響；不能只改 hash |
| blocked／unconfirmed AC | 查看對應問題，補規則、介面、環境或觀測方法後再更新狀態 |
| Missing current independent review rounds | 確認完整已選範圍與目前 digest 已有真實四輪獨立審查 |
| Approval is stale／核可後 digest 改變 | 核對設計是否變動、純核可是否誤寫進設計；變動後對新版本重審 |
| evidence hash mismatch／PASS 被拒絕 | 核對實際步驟、時間、證據與判定，必要時重新執行 |
| 包、基線、RUN 或標籤已存在 | 保留舊版；用新名稱，prepare-review 可安全選擇重用／新建 |
| No changes to checkpoint | 檢查是否確實無變動，或檔案尚未登錄／納入保存範圍 |
| 更新 Skill 後仍沒有新命令 | 專案工具是副本；依 migration.md 保存、比較、明確升級，重跑 init 不會更新 |
| Windows 建立舊測試檔名失敗 | 依 migration.md 的 Windows 說明更新測試資料並在實際環境驗證 |

交付時核對四件事：依據與缺口看得見；案例步驟能照做；成果狀態沒有超過實際證據；原始記錄、進度與版本已按所選模式保存。

## 維護者：行為評測與回饋

修改流程文字後依 [evals/README.md](evals/README.md) 重跑相關情境；重大流程修改跑完整核心集。工具測試與 AI 行為評測分開回報，未跑記 NOT_RUN。一般專案不必執行這套維護評測。實測缺陷回饋與可選度量見 [feedback.md](references/feedback.md)。
