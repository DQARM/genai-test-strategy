# 已確認規則與操作依據
本次由使用者確認：AC-01（Acceptance Criterion，驗收條件）僅已授權鑰匙且控制器距離 ≤ 2.0 m 時允許解鎖，> 2.0 m 拒絕。距離輸入解析度 0.1 m。範圍為距離等號、範圍外拒絕及已授權且範圍內允許。
已確認實驗介面：測試面板有 Reset、Authorized、Distance、Evaluate。Reset 建立鎖定且清空結果歷史；Authorized 設為 true；Distance 以 m 輸入；Evaluate 一次回傳帶本次 cycle 的 allow 值。結果歷史保留先前 cycle。每案記本次 cycle 和 allow；結束 Reset 並確認歷史空白。只驗控制器回應，不承諾物理解鎖。
COV（Coverage，覆蓋項目）01 是剛好 2.0 m；02 是 2.1 m；03 是 1.9 m。均保留。
