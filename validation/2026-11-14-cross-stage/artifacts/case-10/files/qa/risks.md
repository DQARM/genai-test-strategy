# 需求風險評估

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| COV | Coverage | 覆蓋項目 | 表示測試方法導出的分區、邊界、組合或轉移；COV 取自 Coverage |
| DEC | Decision | 決策 | 記錄人的決定與依據 |
| REQ | Requirement | 需求 | 追蹤單一產品需求 |
| RISK | Risk | 風險 | 追蹤失敗情境、影響與取捨 |
| RUN | Run | 測試執行紀錄 | 保存某次實際執行的觀察與證據 |
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
| REQ-001 | 已有初評（待確認） | RISK-001 / OFF after evaluate / control lost | high | 待評估／資料不足 | P1 | 本輪依使用者確認來源的兩份合成回報與失敗日誌重評。已核對一次 evaluate 返回仍為 OFF 的失效回報，另一次供電不可用而未執行 evaluate，屬環境阻塞。沿用 high 嚴重度與 P1 已選優先序，likelihood 仍 unknown、uncertainty 仍 high：全部執行次數、現場暴露量、完整觀測期間與根因未知。這是 AI 更新初評，尚無對此版本的新風險確認；舊評估保留於原基線、執行快照及本機提交。產品規則與需求 revision 1 不變。；依據：SRC-SPEC, SRC-001, SRC-002, SRC-003 | TC-001 |

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
  "severity_rationale": "沿用已採納分級：evaluate 後主輸出仍為 OFF 導致本輪模組控制功能未達承諾。新資料未顯示後果擴大或縮小；不因回報次數變更嚴重度，也不推論範圍外實體設備危害。",
  "likelihood": "unknown",
  "likelihood_rationale": "在 fixture-build-7／synthetic-lab 有一筆附日誌的 FAIL 回報，支持既有失效情境曾在所提供合成紀錄中出現；另一筆 BLOCKED 因供電不可用而未執行 evaluate，不能算產品失敗。全部執行次數、現場暴露量、完整觀測期間及樣本選取方式未知，不能以兩份回報為分母，也不能將單次失效轉成機率或「經常發生」。",
  "uncertainty": "high",
  "priority": "P1",
  "rationale": "保留原已選的輸出控制優先序。此次失效回報強化既有 OFF→evaluate→ON 轉移的回歸價值，但不擴大原範圍或代替人的新取捨。現有 TC-001／COV-001 已有對應斷言；本輪僅更新分析，未操作產品。",
  "source_refs": [
    "SRC-SPEC",
    "SRC-001",
    "SRC-002",
    "SRC-003"
  ],
  "source_citations": [
    {
      "source_id": "SRC-SPEC",
      "reading_seq": 1,
      "finding_index": 1
    },
    {
      "source_id": "SRC-001",
      "reading_seq": 1,
      "finding_index": 2
    },
    {
      "source_id": "SRC-002",
      "reading_seq": 1,
      "finding_index": 2
    },
    {
      "source_id": "SRC-003",
      "reading_seq": 1,
      "finding_index": 1
    }
  ],
  "revision": 2,
  "evidence_refs": [
    "qa/runs/RUN-001.json#/steps/0",
    "qa/evidence/failure.log#L1",
    "qa/runs/RUN-002.json#/steps/0"
  ],
  "owner": "unassigned",
  "residual_risk": "根因、修復情況與可重現頻率未知，尚無修復後新執行證據。供電阻塞沒有獨立診斷 evidence，需由測試／環境負責人確認環境可用，才能取得新產品觀察；目前未指派或承諾時程。此供電問題是環境阻塞線索，不能與產品 FAIL 合計。",
  "assessment_status": "proposed"
}
```

