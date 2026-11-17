# 需求風險評估

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| DEC | Decision | 決策 | 記錄人的決定與依據 |
| Q | Question | 待釐清問題 | 追蹤未決事項、責任人與確認時點 |
| REQ | Requirement | 需求 | 追蹤產品需求；數字為本類流水號 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| SRC | Source | 資料來源 | 追蹤依據文件；本專案 SPEC、HARNESS、NEW 為既有來源標籤，並非數字流水號 |
| TC | Test Case | 測試案例 | 追蹤測試設計；數字為本類流水號 |

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
| REQ-002 | 已有初評（待確認） | RISK-002 / 重啟初始化或殘留狀態使輸出偏離後續確認的規則；目前不能指定何種輸出屬錯誤。 / 重啟恢復行為可能被漏判或被不同人作不同判定；實際產品後果尚未提供。 | 待評估／資料不足 | 待評估／資料不足 | 待評估／資料不足 | 僅初評重啟初始化／殘留狀態風險；產品輸出、觸發及觀測時點未決，嚴重度、可能性與測試優先序均未知。；依據：SRC-NEW | 無 |

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

### RISK-002

```json
{
  "id": "RISK-002",
  "requirement_ids": [
    "REQ-002"
  ],
  "origin": "requirement",
  "assessment_status": "proposed",
  "failure": "重啟初始化或殘留狀態使輸出偏離後續確認的規則；目前不能指定何種輸出屬錯誤。",
  "impact": "重啟恢復行為可能被漏判或被不同人作不同判定；實際產品後果尚未提供。",
  "severity": "unknown",
  "severity_rationale": "重啟輸出承諾與使用影響未定義。",
  "likelihood": "unknown",
  "likelihood_rationale": "沒有重啟實測、缺陷歷史或暴露資料。",
  "uncertainty": "high",
  "priority": "unknown",
  "rationale": "本輪只整理草稿；未有人決定納入正式選測範圍或優先序。",
  "source_refs": [
    "SRC-NEW"
  ],
  "source_citations": [
    {
      "source_id": "SRC-NEW",
      "reading_seq": 1,
      "finding_index": 1
    }
  ],
  "decision_refs": [],
  "evidence_refs": [],
  "disposition": "pending",
  "disposition_reason": "等待產品規則與操作依據，未代表人已接受剩餘風險。",
  "owner": "unassigned",
  "question_ids": [
    "Q-001",
    "Q-002",
    "Q-003"
  ],
  "residual_risk": "重啟後輸出尚無可判定規則，沒有正式案例、實測或驗收證據。"
}
```

