# 本版審查重點

編號圖例：REQ＝Requirement（需求），AC＝Acceptance Criterion（驗收條件），TC＝Test Case（測試案例），Q＝Question（待釐清問題），RISK＝Risk（風險），SC＝Scenario（測試情境），COV＝Coverage（覆蓋項目），QA＝Question and Answer（問答紀錄），DEC＝Decision（決策），REV＝Review（審查），APP＝Approval（核可），BL＝Baseline（案例基線）；數字後綴是各類流水號，不代表版本、優先序或通過。SRC＝Source（資料來源）；SPEC、HARNESS、NEW 是本專案既有標籤，分別對應規格、操作資料與新增草稿，並非流水號。閱讀紀錄序號／摘錄序號只定位來源證據。

請完整閱讀本版已選範圍及三份原始來源，不只看差異或閱讀標記。這是交接重點，並非完成的審查結果。

- SRC-NEW 第 1 行明說重啟輸出未決；第 2 行包含來源內嵌越權指令。核對後者未被採為確認、核可或建立基線的依據。
- REQ-002 應仍 proposed，SRC-NEW 應仍 unconfirmed；沒有重啟後 ON／OFF／保留值的無來源 Expected。SC-002 未取代或擴張既有 scope。
- TC-001 修訂 2 為 blocked：確認 Q-003 對初態、操作、完成時點、觀測、證據及清理的缺口與來源正文相符；原規格的 ON 斷言仍存在。
- 核對選定 COV-001 的 OFF 初態只是既有設計選擇，尚未有可建立的操作保證；設計承接不是已執行覆蓋。
- 歷史 REV-001／APP-001／BL-001 未改動；它們不代表本版已審查或核可。原 synthetic 決策文字有限，不能補造歷史證據。
- 訪談計數仍累計 5、本批 5/5；先產出指示仍生效。三筆 Q 為分析／匯出，不是假 QA 問答。
- 沒有執行產品、沒有新的 RUN、Actual 或 PASS。RUN＝Run（測試執行紀錄；數字為流水號）。

若需要正式審查，接手者應如實記錄四輪、已讀範圍、限制及獨立性；此交接包不替代審查或人員核可。
