# 測試案例設計

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| AC | Acceptance Criterion | 驗收條件 | 追蹤可判定的產品條件；數字為本類流水號 |
| COV | Coverage | 覆蓋項目 | 表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage |
| Q | Question | 待釐清問題 | 追蹤未決事項、責任人與確認時點 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| SC | Scenario | 測試情境 | 表示待選或已選的測試情境 |
| SRC | Source | 資料來源 | 追蹤依據文件；本專案 SPEC、HARNESS、NEW 為既有來源標籤，並非數字流水號 |
| TC | Test Case | 測試案例 | 追蹤測試設計；數字為本類流水號 |

由 cases/*.json 產生。Actual 與執行判定另存 runs；本檔不是執行報告。

## TC-001 — Evaluate changes OFF to ON

狀態：blocked；revision：2

**purpose**

```json
"依既有判準檢查 evaluate 後輸出 ON；保留原 OFF → evaluate → ON 設計目標，初態與操作缺口補齊前不可執行。"
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
  "target": "Synthetic fixture 的隔離狀態；實際可用環境待補",
  "build_binding": "待 Q-003 提供版本辨識方式；執行前須記錄實際受測版本，不把專案 Git 版本當產品版本。",
  "tools": "待 Q-003 提供可用工具與版本；現有文件未提供 fixture v1 的依據。",
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
    "action": "依待補操作指南建立本案專用隔離狀態，記錄環境、工具及受測版本；無指南時停止。",
    "verify": "指南需說明如何確認隔離及必要殘留狀態已清除；目前未具備，不可假定已完成。"
  },
  {
    "action": "建立原選定情境所需的輸出 OFF；reset 是否能達成與實際操作由 Q-003 補足。",
    "verify": "以已確認的 inspect output 介面讀回 OFF 並保存證據；無法建立或讀回則停止，不進行 evaluate。"
  }
]
```

**data**

```json
[
  {
    "name": "initial output",
    "value": "OFF（既有選定情境的設計目標，尚未證實可由 reset 建立）",
    "unit": "discrete",
    "basis": "SRC-HARNESS",
    "source_citations": [
      {
        "source_id": "SRC-HARNESS",
        "reading_seq": 2,
        "finding_index": 1
      }
    ],
    "source_refs": [
      "SRC-HARNESS"
    ],
    "limitations": "此來源僅支持 reset／讀取概念；OFF 來自既有 SC-001／COV-001 設計目標，不表示來源保證 reset 後為 OFF，能力待 Q-003。"
  }
]
```

| 步驟 | 操作／輸入 | 觀測／時機 | Expected／依據 | 證據 |
|---|---|---|---|---|
| 1 | 在本案已獨立建立並確認 OFF 的狀態上，透過待補指南的真實介面執行 evaluate 一次；缺操作指南則停止。 / 無已知外加參數；OFF 為初態而非已確認的 API 參數。 | 該隔離實例的 output；讀取方式與輸出格式待 Q-003 補足。 / evaluate 之後；完成事件及對應觀測方式待 Q-003，不能先假設函式返回即完成。 | output ON（離散值須一致；僅適用 evaluate 之後，不外推為重新啟動後的值） [AC-001, COV-001] | 未來保存初態、evaluate 呼叫／完成與輸出觀測的可對應記錄；格式待指南確認，目前沒有實測證據。 |

**cleanup**

```json
[
  {
    "action": "依待補的清理／重置指南釋放本案隔離狀態及操作資源。",
    "verify": "指南須說明可供下一次獨立重跑的確認方法；現有文件未支持 close fixture 或程序終止方式。"
  }
]
```

**independence**

```json
"每次由本案自行建立、確認與清理隔離初態，不依賴其他案例結果；隔離概念有來源，具體重置及清理待 Q-003。"
```

**verdict_rules**

```json
{
  "pass": "僅在 Q-003 關閉、案例已完成對應審查／核可且實際執行後，初態及完成事件有效、輸出確為 ON 且證據齊全，才可由執行人判定；本次無結果。",
  "fail": "在有效初態、操作完成與可用觀測的前提下，輸出不是 ON 且有對應證據。",
  "inconclusive": "缺完成時機、無輸出或證據不足時無法判定；無法建立初態或操作則登錄 BLOCKED，不判 PASS。"
}
```

**blockers**

```json
[
  "Q-003"
]
```

**automation**

```json
null
```

