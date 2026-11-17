# 測試案例設計

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| AC | Acceptance Criterion | 驗收條件 | 定義可觀測且可判定的產品條件 |
| COV | Coverage | 覆蓋項目 | 表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| SC | Scenario | 測試情境 | 表示待選或已選的測試情境 |
| SRC | Source | 資料來源 | 追蹤文件、操作指南或其他依據 |
| TC | Test Case | 測試案例 | 保存完整前置、步驟、判準與證據要求 |

由 cases/*.json 產生。Actual 與執行判定另存 runs；本檔不是執行報告。

## TC-001 — Evaluate changes OFF to ON

狀態：ready；revision：1

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
      "reading_seq": 1,
      "finding_index": 1
    }
  ]
}
```

**preconditions**

```json
[
  {
    "action": "reset fixture to OFF",
    "verify": "read output OFF"
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
        "reading_seq": 1,
        "finding_index": 1
      }
    ]
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
  "pass": "ON",
  "fail": "not ON with valid input",
  "inconclusive": "no output"
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

