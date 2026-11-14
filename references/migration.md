# 舊專案升級與相容性

僅在專案工具過舊、資料缺新政策或接手舊訪談預算時讀本文件。日常操作依 [workflow.md](workflow.md)，功能沿革見 [CHANGELOG.md](../CHANGELOG.md)。

## 升級專案工具

技能內 scripts/qa_project.py 與專案內 qa/tools/qa_project.py 是兩份檔案。重跑 init 會沿用現有內容，**不會升級工具或遷移資料**。審查端沿用指定版本，升級由設計端處理。

1. 在正確根目錄讀 session、Git 狀態與適用指引，保留原編號、來源及工作內容。比較兩份工具的 `--version`、`--help` 與差異；以實際檔案為準，不從手冊版本猜工具版本。
2. 依 local-versioning.md 保存升級前 checkpoint；保留他人的 staged 內容。記下原工具版本與檢查結果，另備份必要未追蹤／被忽略的證據。
3. 明確以技能內的新工具替換專案工具副本，記新舊版本與改動範圍。僅升級工具不覆寫 registry、cases、原始資料或歷史快照，也不重新初始化專案。
4. 執行新版 `--version`、`--help`、check、render，確認報告及本輪要用的命令。按下表處理真實資料缺口；未知保留，不補造往日閱讀、回答、評分或核可。
5. 保存升級結果及限制。設計內容有變就對新 digest 重審／核可；原基線與 RUN 留在原版。現有產品決策直接沿用，僅新增取捨需要確認。

工具使用 schema 1，已有基線、核可、審查與執行快照保持可讀且不回寫。舊欄位仍可草稿檢查與 render；進入新基線前補足本輪政策所需資料。

## 資料相容性

| 遇到的舊資料 | 續作方式／新基線條件 | 欄位與檢查的完整定義 |
|---|---|---|
| 缺 coverage_items、charters 或設計政策 | 補本輪方法、保留／暫緩覆蓋項目及案例斷言；採 coverage-items-v1，依真實取捨重審 | [test-design.md](test-design.md) |
| 缺需求風險評估／risk_policy | 補本輪需求關聯、分級理由、評估狀態及依據，採 requirement-risk-v1；不從 priority／impact 推成已確認 severity；未選需求可未評估 | [risk-assessment.md](risk-assessment.md) |
| 缺 interactions | 保留歷史缺原文的限制；新問答用 record-qa；有舊摘要不等於有逐字稿 | [interview-records.md](interview-records.md) |
| 缺 readings／source_citations | 按本輪需求實際補讀、追加定位引用，採 source-reading-v1；note／舊摘要／confirmed 標記不能自動轉成閱讀證據 | [source-reading.md](source-reading.md) |
| 缺新版問題／跨領域風險選填欄位 | 舊資料仍可檢查；採用 origin 才按其契約補依據與影響。原來缺關聯的孤立風險不自動豁免 | [spec-review.md](spec-review.md)、[risk-assessment.md](risk-assessment.md) |
| 未使用 execution-profile／selections | 需要排程才新增；保持原 artifacts() 對既有設計欄位的計算範圍 | [execution-selection.md](execution-selection.md) |
| 舊審查包沒有 handoff 或閱讀欄位 | 可人工交接原版本並列限制；舊包保留，新版設計用 prepare-review 建新包。指定歷史包不擅自換版 | [review.md](review.md)、[records.md](records.md) |

純 render 是生成視圖，不會修改設計 digest；新增問答、閱讀、引用、編號字典或決策等 registry／依據內容則會。文件整理與工具升級本身不替人核可，也不要求整個專案重做訪談。

## 舊訪談預算

只轉換可確認為舊預設的三題／十題設定；使用者明訂或來源不明的上限保留。沿用累計題數、原焦點、決策、最新停止／續問選擇；已收尾不因升級重開。

- 舊預設仍進行且未到第一個統整邊界時，可補至五題；例如累計三題再問最多兩題。
- 已到五題邊界而無明確續問選擇時，先統整等待。例如記錄已問 5／10 題，不直接問第六題。
- 超過邊界又無法重建批次時，保留累計，現在統整及選擇一次，不補發多次摘要。
- 人明說「再問最多五題」可作本批依據；泛稱續作不代表重啟訪談。誤計初始化依原問題校正並說明；不明時間／題數／額度保持未知。

轉換後依 [目前的統整與續問規則](workflow.md#統整與續問) 工作，不把舊預設留作新的上限。

## Windows 驗證與舊測試資料

若舊測試在建立「規格 #1?.md」時中斷，是檔名含 Windows 保留字元，尚未測到 HTML 連結。現行共用測試使用合法的中文、空白、#、% 與 & 檔名；? 變體只在非 Windows 執行。這是測試資料修正，不更改產品規則。

在技能目錄執行 `py -3 -m unittest discover -s scripts -p "test_qa_project.py" -v`。Symlinks unavailable 或其他 skipped 依實際原因記錄，不當通過；Linux 成功不代表已完成 Windows 驗證。保留升級前版本及可重現錯誤，按實際環境修復再驗證。
