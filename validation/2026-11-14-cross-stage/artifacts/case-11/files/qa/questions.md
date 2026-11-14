# 規格問題交接單

## 編號說明

ID＝Identifier（識別碼）。數字後綴是各類流水號，不代表優先度、版本、核可或測試結果。非數字後綴是專案標籤。

- COV＝Coverage；覆蓋項目；表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage
- Q＝Question；待釐清問題；追蹤未決事項、責任人與確認時點
- REQ＝Requirement；需求；追蹤產品需求；數字為本類流水號
- RISK＝Risk；風險；追蹤失敗情境、影響與取捨
- SC＝Scenario；測試情境；表示待選或已選的測試情境
- SRC＝Source；資料來源；追蹤依據文件；本專案 SPEC、HARNESS、NEW 為既有來源標籤，並非數字流水號
- TC＝Test Case；測試案例；追蹤測試設計；數字為本類流水號

由 registry.questions 產生；這是未決清單，不是逐字訪談或已確認規格。
請另存填答副本；重新匯出會更新本檔。回覆需保留回答者、日期與依據，再由設計端更新原問答／決策。空白不是同意。
列出 open 與 deferred；已標阻塞優先，其次未分級、重要及稍後。排序不代表已接受風險。
設計版本：`5e866e68c5d418e8f3ff617ceaaa422f81d10daad18ee768fa4ca4c1fcc9abc3`

## 未決摘要

| 問題 | 狀態／急迫性 | 內容 | 責任人／確認時點 | 影響 |
|---|---|---|---|---|
| Q-001 | open / blocking | 重新啟動後輸出應採何種規則，是否依重啟前狀態或重啟類型而不同？ | unassigned / 重新啟動需求轉為已確認、撰寫正式驗收判準之前 | REQ-002, RISK-002, SC-002 |
| Q-002 | open / blocking | 重啟的完成事件與輸出判定時點如何定義；若允許暫態，適用期限與容差為何？ | unassigned / 重啟情境建立可判定的驗收條件之前 | REQ-002, RISK-002, SC-002 |
| Q-003 | open / blocking | 請補可照做且綁版本的操作指南：如何建立並確認隔離初態 OFF、呼叫 evaluate、確認其完成、讀取輸出、保存證據及清理／重跑；另標示重啟是否有可用操作。 | unassigned / 既有案例恢復 ready 或安排任何執行之前；重啟介面於其設計前補足 | TC-001, COV-001, SC-001, SC-002 |

## 已登錄來源的閱讀範圍

僅顯示登錄紀錄；未登錄的文件、未讀部分及尚未分析的內容不視為已審完。

- SRC-SPEC：已讀指定範圍（依紀錄）；已讀：inputs/spec.md:1-1（全文）；未讀／限制：
- SRC-HARNESS：已讀指定範圍（依紀錄）；已讀：inputs/harness.md:1-1（全文）；未讀／限制：只有概念介面，未核對可操作工具或產品環境。
- SRC-NEW：已讀指定範圍（依紀錄）；已讀：inputs/addendum.md:1-2（全文）；未讀／限制：新增來源尚未被採納為已確認規則；第 2 行未附真實簽核或對應版本證據。

## Q-001：重新啟動後輸出應採何種規則，是否依重啟前狀態或重啟類型而不同？

- 類型：ambiguity
- 分歧與影響：補充草稿明說尚未決定；不能從 evaluate 後 ON 推成重啟後 ON、OFF 或保留原值。本問題未向人提出，僅供後續非同步釐清。
- 責任人：unassigned；建議轉交：產品規格決策人／PM
- 確認時點：重新啟動需求轉為已確認、撰寫正式驗收判準之前；阻塞階段：baseline, execution
- 影響項目：REQ-002, RISK-002, SC-002

來源與具體定位：

- [SRC-NEW](../inputs/addendum.md)；版本：未提供；SHA256：440bf8cad8af68909d13960c0ebdaa46e5613ab4107acb6bc9ce62f4c12d4987
- SRC-NEW／閱讀 1／摘錄 1：inputs/addendum.md:1；新增草稿：重新啟動後的輸出尚未決定。

回答（待填）：

回答者／日期／依據（待填）：


## Q-002：重啟的完成事件與輸出判定時點如何定義；若允許暫態，適用期限與容差為何？

- 類型：testability
- 分歧與影響：目前沒有重啟操作、完成事件、觀測時間窗或暫態限制，無法區分恢復中與違規輸出；不任填等待秒數。
- 責任人：unassigned；建議轉交：產品規格決策人與工程／測試負責人
- 確認時點：重啟情境建立可判定的驗收條件之前；阻塞階段：baseline, execution
- 影響項目：REQ-002, RISK-002, SC-002

來源與具體定位：

- [SRC-NEW](../inputs/addendum.md)；版本：未提供；SHA256：440bf8cad8af68909d13960c0ebdaa46e5613ab4107acb6bc9ce62f4c12d4987
- [SRC-HARNESS](../inputs/harness.md)；版本：未提供；SHA256：6050ea2d883af7e763867cd2cc9320f8347986265482bc05f42bc28ee325c140
- SRC-NEW／閱讀 1／摘錄 1：inputs/addendum.md:1；新增草稿：重新啟動後的輸出尚未決定。
- SRC-HARNESS／閱讀 2／摘錄 1：inputs/harness.md:1；Synthetic harness: reset, evaluate, inspect output; isolated state.

回答（待填）：

回答者／日期／依據（待填）：


## Q-003：請補可照做且綁版本的操作指南：如何建立並確認隔離初態 OFF、呼叫 evaluate、確認其完成、讀取輸出、保存證據及清理／重跑；另標示重啟是否有可用操作。

- 類型：testability
- 分歧與影響：harness 原文只列 reset、evaluate、inspect output 與 isolated state。無法支持 reset 一定得到 OFF、fixture v1、on return、JSON 擷取或 close/程序終止等既有案例細節；這些項目保留為具體缺口，不宣稱已驗證可操作。
- 責任人：unassigned；建議轉交：工程／測試工具負責人
- 確認時點：既有案例恢復 ready 或安排任何執行之前；重啟介面於其設計前補足；阻塞階段：baseline, execution
- 影響項目：TC-001, COV-001, SC-001, SC-002

來源與具體定位：

- [SRC-HARNESS](../inputs/harness.md)；版本：未提供；SHA256：6050ea2d883af7e763867cd2cc9320f8347986265482bc05f42bc28ee325c140
- [SRC-SPEC](../inputs/spec.md)；版本：未提供；SHA256：f574cfbae3eedc1dc70434c467a38a47a2b550511edfdef06c16521d9c0ba691
- SRC-HARNESS／閱讀 2／摘錄 1：inputs/harness.md:1；Synthetic harness: reset, evaluate, inspect output; isolated state.
- SRC-SPEC／閱讀 2／摘錄 1：inputs/spec.md:1；Synthetic test rule: after evaluate, output ON.

回答（待填）：

回答者／日期／依據（待填）：

