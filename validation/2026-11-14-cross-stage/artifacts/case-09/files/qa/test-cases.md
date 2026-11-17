# 測試案例設計

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| AC | Acceptance Criterion | 驗收條件 | 定義可觀測且可判定的產品條件 |
| COV | Coverage | 覆蓋項目 | 表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage |
| DEC | Decision | 決策 | 記錄人的決定與依據 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| SC | Scenario | 測試情境 | 表示待選或已選的測試情境 |
| SRC | Source | 資料來源 | 追蹤文件、操作指南或其他依據 |
| TC | Test Case | 測試案例 | 保存完整前置、步驟、判準與證據要求 |

由 cases/*.json 產生。Actual 與執行判定另存 runs；本檔不是執行報告。

## TC-001 — Evaluate changes OFF to ON

狀態：ready；revision：2

**purpose**

```json
"Detect missing output"
```

**ac_ids**

```json
[
  "AC-001"
]
```

**risk_ids**

```json
[
  "RISK-001"
]
```

**scenario_ids**

```json
[
  "SC-001"
]
```

**coverage_ids**

```json
[
  "COV-001"
]
```

**environment**

```json
{
  "target": "isolated fixture",
  "build_binding": "record fixture version at run",
  "tools": "fixture v1",
  "binding_refs": [
    "SRC-HARNESS"
  ],
  "source_citations": [
    {
      "source_id": "SRC-HARNESS",
      "reading_seq": 2,
      "finding_index": 1
    }
  ]
}
```

**preconditions**

```json
[
  {
    "action": "以既有 harness 執行 reset；在 evaluate 前執行 inspect output。",
    "verify": "初態讀值 output 必須明確等於 OFF；讀值不等於 OFF 時停止本案並記錄初態不成立，無讀值或無法觀測時記為無法判定。初態確認完成後才執行 evaluate。",
    "evidence": "保存 evaluate 前 inspect output 的 fixture JSON 或原始讀值，標示為初態證據，並於實際執行時記錄 fixture 版本。",
    "decision_refs": [
      "DEC-002"
    ]
  }
]
```

**data**

```json
[
  {
    "name": "initial",
    "value": "OFF",
    "unit": "discrete",
    "basis": "SRC-HARNESS",
    "source_citations": [
      {
        "source_id": "SRC-HARNESS",
        "reading_seq": 2,
        "finding_index": 1
      }
    ],
    "decision_refs": [
      "DEC-002"
    ],
    "note": "OFF 是本案既有初態目標與本輪處置明確要求的讀值；harness 文件支持 reset／inspect 操作，不據此推導重啟後行為。"
  }
]
```

| 步驟 | 操作／輸入 | 觀測／時機 | Expected／依據 | 證據 |
|---|---|---|---|---|
| 1 | evaluate once / OFF | output / on return | output ON [AC-001, COV-001] | capture fixture JSON |

**cleanup**

```json
[
  {
    "action": "close fixture",
    "verify": "process terminated"
  }
]
```

**independence**

```json
"fresh process each case"
```

**verdict_rules**

```json
{
  "pass": "初態證據確認 output=OFF，evaluate 一次正常返回，且輸出證據確認 output=ON。",
  "fail": "已確認有效 OFF 初態且 evaluate 正常返回，但可觀測輸出不是 ON。",
  "inconclusive": "初態未能確認為 OFF、觀測無效或缺少輸出／必要證據時，不作產品通過或失敗結論；初態或操作建立失敗可於實測另記 BLOCKED。"
}
```

**blockers**

```json
[]
```

**automation**

```json
null
```

