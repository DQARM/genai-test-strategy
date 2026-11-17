可以接回，但需求應保持 `proposed`。原決策時間確實無法取得時，保留這項限制，不以登錄時間代填，也不新增缺資料的決策。以下僅提供草稿，沒有建檔或修改專案。

編號說明：QA＝Question and Answer（問答紀錄）；QA-012 的 012 是第 12 筆紀錄流水號，不代表累計已問需求題數。REQ＝Requirement（需求）、Q＝Question（待釐清事項）、DEC＝Decision（決策）；新編號須沿用專案各類下一個未使用流水號。

**既有問答：保留原筆，不另造一次回答**

`registry.interactions` 中 QA-012 應保留以下內容；其他既有欄位沿用：

```json
{
  "id": "QA-012",
  "question_text": "匯出成功後原設定應怎樣？",
  "answer_text": "維持原設定",
  "answer_status": "answered",
  "capture": "verbatim",
  "asked_at": null,
  "answered_at": null,
  "answered_by": "使用者"
}
```

時間缺失不等於原文缺失，因此不改成 `summary_only`。若原筆已保存，只在後續記錄實際建立後補入 `related_ids`；原話及既有解讀不覆寫。實際補登時的 `recorded_at`／`answer_recorded_at` 僅表示登錄時間。

**需求草稿：尚未具備完整確認紀錄**

以下編號是佔位文字，不是可直接匯入的正式編號：

```json
{
  "id": "<需求編號>",
  "text": "匯出成功後，維持原設定。",
  "revision": 1,
  "status": "proposed",
  "source_refs": [],
  "decision_refs": [],
  "confirmation": null
}
```

這是依原問答整理的需求文字。透過 QA-012 的 `related_ids` 連回需求；不把 QA 編號放進 `decision_refs`，也不虛構決策檔案或確認依據。

**限制紀錄：追蹤阻塞，不再向你提問**

| 欄位 | 草稿內容 |
|---|---|
| `id` | `<限制編號>`，使用 Q 類下一個未用編號 |
| `text` | 歷史回答原文可用，但原決策時間確定無法取得；目前缺少符合契約的規則確認紀錄。 |
| `status` | `deferred` |
| `owner` | `unassigned` |
| `due_or_trigger` | 原時間不再列為追查事項；日後若另有有權決策者的明確採納，再以該次真實決策時間建立新紀錄。 |
| `impact_ids` | `["<需求編號>"]` |
| `blocks` | `["baseline", "execution"]`，限依賴此規則的正式驗收 |
| `decision_refs` | `[]` |

session 可補上這段草稿：

> 沿用 schema_version=1。歷史問答接回不增加訪談題數，保留原有進度及停止提問狀態。QA-012 的原始時間未知且不可取得；需求保持 proposed，本輪不新增 DEC 或 confirmation。未進行檔案保存、檢查、審查或實測。後續若發生新的明確採納，由實際決策者提供決定，記錄者保存新決策及其當下時間，不回填歷史時間。
