# 執行安排、Smoke 與回歸選取

只在使用者要安排執行或評估變更影響時讀本頁；設計手動案例不必先填排程資料。Smoke 是核心路徑的快速檢查，Regression（回歸）是確認既有行為未被變更破壞；兩者範圍都由本專案定義，不是自動放行證據。

## 與設計分開保存

新增選填 `qa/execution-profile.json`，保存案例執行優先序、標籤、預估分鐘、是否為自動化候選及排程備註。下列是格式示意；ID 必須換成既有案例，時間與排序須有本專案依據，不是預設值：

```json
{
  "schema_version": 1,
  "priority_order": ["P1", "P2"],
  "cases": {
    "TC-001": {
      "priority": "P1",
      "tags": ["smoke", "regression"],
      "estimated_minutes": 15,
      "automation_candidate": false,
      "note": "人工操作；設備切換另計"
    }
  }
}
```

TC＝Test Case（測試案例），SEL 取自 Selection（執行選取建議），REQ＝Requirement（需求），RISK 是 Risk（風險）；數字後綴為各類流水號。P 取自 Priority（優先序），P1／P2 的定義與數字方向由專案決定，與流水號不同。

`priority_order` 明列由優先到後，沒有就不猜代碼方向。案例未覆寫 priority 時，可依已連結風險在此排序中的最高優先序安排；未知或不在排序內的風險另列，不當低風險。`estimated_minutes` 可省略或 null；零、負數、布林值、無限大不可當時間。automation_candidate 僅是候選，不能據此把 type 改 automated 或假稱已有腳本。檔案可完全不建立。

此檔與選取結果不進原 `artifact_digest`，各自綁版本；修改它不使案例設計審查過期。**原有 registry、案例所有欄位、strategy.md、plan.md 與原證據仍按原規則進 digest**；不能把判準、操作、設計範圍、風險取捨移到此檔以繞過審查，也不自動搬走舊案例欄位。

## 產生建議清單

工具 1.9.0，以下在專案根目錄執行；Windows 可將 python 改為 py -3：

```text
python qa/tools/qa_project.py select-cases .
python qa/tools/qa_project.py select-cases . --tag smoke
python qa/tools/qa_project.py select-cases . --changed REQ-001 --tag smoke --budget-minutes 60 --save SEL-001
python qa/tools/qa_project.py check-selection . --id SEL-001
```

- 無條件時讀既有 selected_case_ids；`--changed`、`--tag` 可重複。變更依已登錄的來源／決策／規則／風險／情境／覆蓋／問題影響關係傳到案例。程式 diff 本身不會自動變成需求關聯，AI 須先查實際變更並提供已有 ID。
- 變更命中與標籤採**聯集**，即加入 smoke 保底案例，不把受影響案例用標籤過濾掉。retired 另列排除原因；draft／blocked 保留並標狀態，不能宣稱可執行。
- 輸出理由、是否屬原設計範圍、風險、排序依據、未知優先序／時間、預算狀態、缺引用及未映射變更。無命中不代表無影響；缺共同環境或隱藏依賴時要人工補評估。
- 預算只比較已知估計，不自動刪案例。unknown 時不能說時間足夠，within-estimate 也只代表案例估計加總，另計設備切換／準備／排錯。超時先提出取捨與剩餘風險，真實決策才改設計範圍。
- `--save` 寫入不可覆寫的 `qa/selections/SEL-001.json`；省略則只回傳 JSON。AI 依結果提供簡短閱讀表，不維護第二套清單。要改安排使用新 ID。
- `check-selection` 核對完整設計、排程檔及來源原檔指紋；不檢查選取語意，不代表核可。任何一項已變就重新產生，保留舊建議。選取時已報來源缺失／過期，即使之後指紋相同也仍須處理警示。

先以高價值／高危害失效安排足夠方法與證據，再考慮時間、設備與人力；不能只挑便宜或短的案例。未涵蓋本輪已選風險會列清單，接受哪些剩餘風險仍由人決定。選取建議不修改 registry.scope，不建立核可基線、不啟動測試；實際執行仍需依既有授權、環境與 run 規則留證據。

select-cases 不是設計檢查器；狀態欄是現有記錄，不保證內容完整。執行前仍須 check、處理實際阻塞及確認環境，不可只看到清單裡寫 ready 就開始操作設備。
