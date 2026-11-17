# 輸出控制測試策略：本輪修正

編號圖例：REQ＝Requirement（需求）、AC＝Acceptance Criterion（驗收條件）、RISK＝Risk（風險）、SC＝Scenario（情境）、COV＝Coverage（覆蓋項目）、TC＝Test Case（測試案例）、F＝Finding（審查發現）、Q＝Question（待釐清問題）、DEC＝Decision（決策）、SRC＝Source（來源）；數字是各類流水號，SRC-SPEC 與 SRC-HARNESS 的文字後綴是既有來源標籤。

## 已知條件與依據

本輪沿用輸出控制焦點及既有範圍：模組的 OFF → evaluate → ON，實體設備不在本輪範圍。REQ-001、AC-001 的 evaluate 後 ON 規則沿用既有確認；RISK-001、SC-001、COV-001、TC-001 的選取不變。

已實讀 `inputs/spec.md` 與 `inputs/harness.md` 第 1 行全文，追加來源閱讀紀錄 2。SRC-SPEC 指紋為 `f574cfbae3eedc1dc70434c467a38a47a2b550511edfdef06c16521d9c0ba691`；SRC-HARNESS 指紋為 `6050ea2d883af7e763867cd2cc9320f8347986265482bc05f42bc28ee325c140`。規格支持 evaluate 後 ON；harness 列 reset、evaluate、inspect output 及隔離狀態。原文沒有重啟輸出規則，也沒有新增命令或 API 可供推定。

## 方法與本輪變更

沿用單元層、人工操作與狀態轉移方法；COV-001 由 TC-001 的 evaluate 後 ON 斷言承接。依 DEC-002 修正 F-001：初態須在 reset 後、evaluate 前讀到 output=OFF，並留存初態證據。OFF 是既有案例的初態目標與本輪處置要求，不宣稱 harness 原文另有 reset 後必為 OFF 的產品承諾。

此次不新增自動化命令；既有合成 fixture 的操作名稱保持不變。建立或觀測初態失敗不判產品 FAIL；只有有效初態、有效操作及可觀測輸出才能套用既有驗收判準。原有清理與隔離步驟沿用。

## 品質與剩餘缺口

功能正確性及初態可觀測性與本輪直接相關；性能、實機效果與重啟恢復沒有本專案判準，不擴張為新 Expected。F-002 對應 Q-001，仍為未決；現有 evaluate 案例不包含重啟。若日後納入重啟案例，須先取得應然輸出、觀測時機及適用重啟條件。責任人未指派，未接受重啟剩餘風險。

本輪交付是案例修訂及待審交接。結構檢查、初態文字修正及 ready 標記均不代表獨立審查、人的新版核可、產品實測或放行。
