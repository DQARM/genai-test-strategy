# 待審案例
TC（Test Case，測試案例）01 宣稱 COV-01、AC-01：Reset 並確認鎖定、歷史空白；Authorized=true；Distance=1.9；Evaluate，核對本次 cycle 的 allow=true 並記錄；結束 Reset 確認清空。
TC-02 宣稱 COV-02、AC-01：先獨立 Reset、核對初態；Authorized=true，Distance=1.9，Evaluate 確認 allow=true 作準備。再改 Distance=2.1，Evaluate；只檢查結果歷史存在 allow=true 就判 PASS，不核對本次 cycle。保存輸入與歷史畫面。結束 Reset 確認空白。
TC-03 宣稱 COV-03、AC-01：獨立 Reset 確認鎖定及歷史空白；Authorized=true，Distance=1.9，Evaluate；檢查同次 cycle 的 allow=true，否則 FAIL；無本次回應則無法判定；記輸入、初態、cycle、allow；結束 Reset 確認清空。全部只是設計，尚未執行。
