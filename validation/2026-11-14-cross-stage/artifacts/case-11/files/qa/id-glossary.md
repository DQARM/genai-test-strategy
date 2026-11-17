# 專案編號字典

由工具預設慣例與 registry.project.id_glossary 產生；修改來源字典後重新 render。

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| AC | Acceptance Criterion | 驗收條件 | 追蹤可判定的產品條件；數字為本類流水號 |
| APP | Approval | 核可紀錄 | 記錄人對明確內容與範圍的核可 |
| BL | Baseline | 案例基線 | 凍結已核可的案例版本 |
| COV | Coverage | 覆蓋項目 | 表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage |
| DEC | Decision | 決策 | 記錄人的決定與依據 |
| EXP | Exploration | 探索任務 | 限定探索目的、時間與觀察；EXP 取自 Exploration |
| F | Finding | 審查發現 | 追蹤具體問題與處置 |
| Q | Question | 待釐清問題 | 追蹤未決事項、責任人與確認時點 |
| QA | Question and Answer | 問答紀錄 | 成對保存提問、選項、原始回答與獨立的 AI 解讀 |
| REQ | Requirement | 需求 | 追蹤產品需求；數字為本類流水號 |
| REV | Review | 審查紀錄 | 記錄特定版本的案例審查 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| RUN | Run | 測試執行紀錄 | 保存某次實際執行的觀察與證據 |
| SC | Scenario | 測試情境 | 表示待選或已選的測試情境 |
| SEL | Selection | 執行選取建議 | 依變更與標籤提出案例清單，不改設計範圍或代表已核可 |
| SRC | Source | 資料來源 | 追蹤依據文件；本專案 SPEC、HARNESS、NEW 為既有來源標籤，並非數字流水號 |
| TC | Test Case | 測試案例 | 追蹤測試設計；數字為本類流水號 |
| UTF | 待確認 | 待確認 | 請確認本專案定義，不猜測英文來源 |

