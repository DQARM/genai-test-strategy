# 修訂版審查重點

編號圖例：REV＝Review（審查）、F＝Finding（審查發現）、TC＝Test Case（測試案例）、Q＝Question（待釐清問題）、DEC＝Decision（決策）、QA＝Question and Answer（原始問答紀錄）；數字為各類流水號。

1. 核對 TC-001 修訂 2 的 reset 後、evaluate 前 output=OFF 讀值、觀測證據及初態失敗判定是否足以處理 REV-001／F-001。回到原始 harness、DEC-002 及 QA-006 核對；不得把初態目標誤說為 harness 明文產品規則。
2. F-002 保持 open，Q-001 保留未決的重啟後輸出、觀測時機及適用條件。沒有重啟 Expected、風險接受或使用者新版核可；不要因初態採 OFF 推導重啟後也應 OFF。
3. 對本包完整選定範圍完成四輪審查，不能只審差異。舊審查 digest 不套用新版；修正完成不等於新版本已審。
4. QA-006 只有使用者主動提供的原話；原題／選項不可見。既有 QA-005 僅見 session 摘要，沒有補造原文。歷史核可與基線保留原檔，本輪無產品實測。
