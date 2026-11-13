# 版本沿革

本文件保存功能沿革；使用目前流程見 [README.md](README.md)，舊專案處理見 [migration.md](references/migration.md)。手冊與 Python 工具的版號分開。

## 手冊 1.21.0 — 2026-11-13

- 整理 SKILL.md 為入口、核心界線與按需讀取路線；workflow.md 集中初始化、訪談節奏、保存及續作規則。
- templates.md 保留欄位與示例，README 保留使用 SOP；版本史與舊預算／工具升級移至獨立文件。
- 日常文件以目前能力描述，移除過期版號前綴；保留必要的舊專案相容性入口。
- Python 工具維持 1.9.0，資料 schema、命令、整份設計 digest、來源引用、COV 模型、審查包、核可及執行快照皆未變更。
- 審查手冊 1.5.1 同步整理版本措辭，保留可獨立使用的四輪準則；可攜包仍附完整準則及回傳模板。

## 工具功能沿革

以下從既有文件彙整，未確認的發佈日期不補寫。

| 工具版本 | 功能 |
|---|---|
| 1.9.0 | export-questions、跨領域風險、select-cases／check-selection；執行安排與設計版本分開。對應設計手冊 1.20.0、審查手冊 1.5.0 |
| 1.8.0 | prepare-review、resolve-review、check-review-pack、自動延續包編號及可攜 ZIP；交接協定 2，專案 schema 維持 1 |
| 1.7.0 | readings、source_citations、record-reading／show-source、閱讀視圖與 source-reading-v1 |
| 1.6.0 | interactions、record-qa／show-qa、原始問答與更正鏈的閱讀視圖 |
| 1.5.0 | 需求直接風險關聯、severity 與評估狀態、requirement-risk-v1、風險報告 |
| 1.4.0 | 審查包 handoff 欄位與 genai-test-review 交接；schema 1 及基線條件延續 |
| 1.3.0 | 方法／coverage_items、charters、共用及推導判準、coverage-items-v1、設計報告 |
| 1.2.0 | 離線 report.html 與來源／案例雙向連結，原 Markdown 輸出保留 |
| 1.1.0 | 生成視圖編號說明、id-glossary.md |
| 1.0.0 | 本機專案工具與原有 schema 1 基礎流程 |

## 其他既有修正

- 早期手冊 1.9.1 記錄 Windows 測試檔名修正：共用測試改用合法字元，? 變體限非 Windows；未因此改 qa_project.py 版本。
- 訪談節奏由舊預設三題／十題改為每五題統整並選擇續問或先產出；使用者明訂限制仍優先。舊進度轉換集中在 migration.md。
