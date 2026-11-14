# 需求風險評估

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| DEC | Decision | 決策 | 記錄人的決定與依據 |
| REQ | Requirement | 需求 | 追蹤單一產品需求 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| SRC | Source | 資料來源 | 追蹤文件、操作指南或其他依據 |
| TC | Test Case | 測試案例 | 保存完整前置、步驟、判準與證據要求 |

由 registry.json 產生。評估狀態與需求確認狀態分開；未知不等於低風險，案例連結不是實測證據。

## 分級準則

```json
{
  "status": "confirmed",
  "decision_refs": [
    "DEC-001"
  ],
  "severity": {
    "high": "Synthetic main function lost",
    "low": "Synthetic cosmetic effect"
  },
  "likelihood": {
    "high": "Observed often in synthetic fixture",
    "low": "Rare in synthetic fixture"
  },
  "priority": {
    "P1": "Selected synthetic scope",
    "P2": "Later synthetic scope"
  }
}
```

| 需求 | 評估狀態 | 風險／失敗情境／後果 | 嚴重度 | 可能性 | 測試優先序 | 評估說明 | 關聯案例 |
|---|---|---|---|---|---|---|---|
| REQ-001 | 已確認 | RISK-001 / OFF after evaluate / control lost | high | 待評估／資料不足 | P1 | Synthetic assessment of missing control；依據：DEC-001 | TC-001 |

## 風險詳情與依據

### RISK-001

```json
{
  "id": "RISK-001",
  "failure": "OFF after evaluate",
  "impact": "control lost",
  "requirement_ids": [
    "REQ-001"
  ],
  "severity": "high",
  "severity_rationale": "Main output unavailable",
  "likelihood": "unknown",
  "likelihood_rationale": "No field data",
  "uncertainty": "high",
  "priority": "P1",
  "rationale": "selected promise",
  "source_refs": [
    "SRC-SPEC"
  ],
  "source_citations": [
    {
      "source_id": "SRC-SPEC",
      "reading_seq": 1,
      "finding_index": 1
    }
  ]
}
```

