# 成對問答紀錄

QA＝Question and Answer（問答紀錄），Q＝Question（待釐清問題），DEC＝Decision（決策）；數字後綴是各類流水號，不代表確認狀態。QA 不是品質保證的縮寫；一筆 QA 記一次提問與回覆，一個 Q 可有多筆問答，回答本身不等於決策。

## 保存與讀取

- 在可寫的專案中，提問時先保存原始問題、必要情境及實際呈現的完整選項，answer_status=pending；收到回答後，先原樣保存，再另寫 interpretation（AI 解讀）。「第二個」「是」保留原話及當時選項，不只保存展開後的摘要。「不知道」也要記錄，不能略過。
- 每題用同一筆 QA 完成原本 pending 的回答；不得改寫原問題或選項。已回答後的改口或 AI 解讀修正，新增 QA，以 supersedes 指向上一筆，記 change_reason，保留舊紀錄並檢視受影響的決策、規則、風險與案例。只有新增關聯可在原筆補 related_ids，不刪原關聯。
- 已有草稿／口頭規則、初始化與續問選擇也可記錄；kind 區分 setup、clarification、checkpoint、correction。只有既有流程認定的需求決策題計入額度，不因新增紀錄、補登或更正而重算題數。初始化前的問答在取得專案存取後，依仍可見原文補登；不重問。
- 使用者主動補充、原問題／選項已不可見、舊資料只剩摘要時，保留實際可見的原文，其餘為 null 並寫缺失原因。不得根據摘要、記憶或推測補寫逐字稿。缺少原文不重啟訪談；有必要分歧才依原本額度及續問選擇處理。
- 原始問答存 registry.interactions；決策在 decisions，透過 interaction_refs 指回實際問答；session 只存目前狀態、QA 編號及定位。不要另外維護一份逐字稿真相，也不要每題載入所有問答。用 show-qa 索引挑選後，再讀單筆原文及相關決策。
- 依 [workflow.md 的統整時機](workflow.md#統整與續問)，只呈現新增／變更的規則、重要解讀、未決與可交付內容，不重貼全部問答，也不逐題加一個「是否理解正確」確認關卡。繼續訪談的選擇不等於核可規則。
- 對話限定模式不建立檔案、不宣稱保存；之後獲授權才轉存可見內容。完整聊天匯出屬選配，不是預設前置工作。

## 結構與命令

使用支援 record-qa 的專案工具；舊版依 [migration.md](migration.md) 升級。schema 1 的 interactions 為選填陣列，缺欄位的舊專案仍可檢查與閱讀，不自動捏造歷史。

以下是尚未提問的填寫模板，不可直接當成真實訪談；填入實際內容後才記錄：

```json
{
  "id": "QA-001",
  "kind": "clarification",
  "question_id": null,
  "question_text": "實際向使用者提出的完整問題與必要情境",
  "options": [],
  "answer_text": null,
  "answer_status": "pending",
  "capture": "verbatim",
  "missing_reason": null,
  "asked_at": null,
  "answered_at": null,
  "answered_by": null,
  "interpretation": null,
  "related_ids": [],
  "supersedes": null,
  "change_reason": null
}
```

- question_id：已有問題清單時填真實 Q 編號；無對應未決問題時可 null，不為初始化硬建 Q。options 必須存在，無選項才用空陣列；有選項保留原順序、文字及差異說明。題目中的 AI 建議也要保留其「建議」標示。
- answer_status：pending（未回答）、answered（已回答）、partial（只回答部分）、unknown（使用者不知道）、deferred（使用者暫緩）、unavailable（缺原始回答）。與規則 confirmed 分開；partial 只能採納確實回答的部分。
- capture：verbatim（提問與回答原文可用；未答時只有提問）、partial（部分原文缺失）、summary_only（僅剩摘要）。後兩者必填 missing_reason。summary_only 的 question_text、answer_text 必須 null，options=[]；摘要只放 interpretation。unavailable 的 answer_text=null；不把缺原文寫成使用者回答「不知道」。
- asked_at／answered_at 是真正對話時間，未知填 null；answered_by 依已知身分，僅知是使用者就寫「使用者」，不知道就 null，不虛構姓名。工具自動補 recorded_at／answer_recorded_at 作為登錄時間，不冒充原對話時間。
- interpretation：AI 對回答的解讀，明列條件、尚未回答部分及未決事項；不是逐字原話或自動核可。related_ids 指向已存在的需求、風險、案例、問題或決策，用來反查影響，不表示那些內容已獲確認。
- supersedes：需更正時指向同一條更正鏈最後一筆 QA；change_reason 記實際更正內容與已知原因，不捏造改口理由。不修改已完成的原始問答，也不把原本範圍不同的回答強行互相取代。

將輸入寫為專案內 UTF-8 JSON（可用暫存輸入檔），由工具保存；內容也可由標準輸入傳入，避免 shell 拼接使用者原話：

```bash
python qa/tools/qa_project.py record-qa . --input qa/qa-input.json
python qa/tools/qa_project.py show-qa .
python qa/tools/qa_project.py show-qa . --id QA-001
```

record-qa 新增紀錄，或把原筆 pending 完成為已回答；完成時保留原題、選項與登錄時間，補回答／解讀。已回答紀錄只能補關聯；修改原話或解讀必須新增更正紀錄。輸入檔只是傳遞副本，寫入成功後移除代理自己建立的暫存檔，不保留另一份可編輯真相。--input - 可直接讀標準輸入。show-qa 未指定編號只列精簡索引，不印完整回答。

## 決策、檢查與閱讀

1. 保存問答後，僅依實際決策更新規則；decisions.interaction_refs 可列 QA 編號。保留真實 by／at／evidence_ref；決策 Markdown 可寫決策內容及問答定位，不必複製整段原話。仍要核對原始回答是否支持每一項適用條件。未答／不知道／暫緩／缺回答不可作 confirmed 決策依據。
2. check 驗證狀態、必填原文、缺失標示、時間格式、引用及更正鏈；不完整原文與引用舊答案會警示。結構檢查不能確認紀錄與宿主對話逐字一致、沒漏記或取得身分認證。工具不是自動攔截全部聊天，代理必須實際執行保存。
3. render 產生 qa/interview.md 與 report.html 的「問答紀錄」，區分原話與 AI 解讀，標出已被更正的紀錄，可從案例／需求／風險／決策點回問答及反查；不按文字相似度編造關聯。這些視圖不直接編輯。
4. 問答納入 registry 的既有設計 digest；新增、更正或補關聯會使舊審查／核可不再對應完整現行版本。保留舊基線與執行快照，不回填其內容。只重產視圖不改 digest。
5. review-pack 只帶決策引用、問題及本輪關聯的問答與必要的更正鏈，不帶無關初始化／續問對話。原始問答可核對決策來源，AI 解讀不能取代規格；沿用完整 artifact_digest，不用篩選後內容重算。原文缺失如實列限制。
