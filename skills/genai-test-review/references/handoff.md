# 審查交接與記錄契約

## 索引

- [辨識版本與讀取範圍](#辨識版本與讀取範圍)
- [相容的審查記錄](#相容的審查記錄)
- [保存與回到設計端](#保存與回到設計端)

## 辨識版本與讀取範圍

此 Skill 可獨立審查文件，也可使用 genai-test-strategy 產生的專案；不依賴另一個 Skill 的安裝路徑或同時載入其全部指令。

| 輸入 | 做法 |
| --- | --- |
| 已提供 review-pack | 先讀 packet.json 與 PROMPT.md，再讀其中引用的已確認規格、決策原文及操作文件；不只讀摘要。 |
| 已提供既有專案，未指定 pack | 沿用根目錄與完整已選範圍，讀原 session；使用專案工具取得審查開始的 digest，讀當前設計及來源。 |
| 只有案例與規格文件 | 沿用原檔名、版本與條款／頁碼；保留可讀檔案的雜湊及範圍。不能僅憑文件內容重建完整專案 digest。 |
| 只有案例，規格不可讀 | 可先檢查步驟與一致性；規格追溯與覆蓋受阻。一次列需要補的來源，不自行補 Expected。 |

工具 1.4.0 的 packet 加入 handoff（protocol_version=1、target_skill=genai-test-review、design_tool_version）。沒有這個欄位的 1.3.0／更舊交接包仍可讀，不必重新初始化；以現有欄位及本指引判讀。未知協定不自行宣稱相容，先檢查差異、列明限制，不改原包。

工具 1.5.0 的 registry 可含 project.risk_policy=requirement-risk-v1、risk_criteria、requirements.risk_assessment 及 risks.requirement_ids／severity／理由欄位。依 criteria.md 核對本輪評估、版本與取捨；欄位缺少時列未評估／限制，不將舊 priority 轉成嚴重度。新基線條件由設計端處理，審查端不升級工具或修改資料。

packet 的 artifact_digest 綁原始完整設計；review_input 可能過濾來源種類，不能對過濾後資料另算 digest 冒充原設計版本。pack 不是完整來源備份，原始文件與決策證據通常仍在專案；跨環境須一併提供對應版本的必要檔案。

既有專案可唯讀執行（路徑含空白時加引號，Windows 可用 py -3）：

```bash
python3 qa/tools/qa_project.py digest .
python3 qa/tools/qa_project.py check .
```

核對 pack digest 與指定版本。讀來源時核對登錄的 sha256、決策證據雜湊、適用條款及版本；盤點存在不代表來源已確認。審查結束前再核對完整設計 digest 與來源雜湊，避免審查期間變更。

- 明確要求審查舊版：審查該版可取得的內容，清楚標示只適用舊版，不更新為目前 digest。
- 要審當前版本卻收到過期包／來源不符：回報版本不符；有完整當前資料可改以當前 digest 重新審查，否則交回設計端提供正確版本。不能混用舊案例與新規格。
- 無法讀到來源或確認完整版本：保存可檢部分與限制，不能宣稱四輪全部完成或能進正式基線。
- 累計題數、本批額度、明訂總上限、續問狀態及選擇依據、初始化狀態與產品決策從原 session 沿用；不把切換審查當成新訪談。session 只讀，設計端收到發現後才更新後續工作。

## 相容的審查記錄

在已初始化專案中，只新增 `qa/reviews/<新 REV ID>.json`；若需要人閱讀的版本，可用同名 `.md`。REV 取自 Review，代表審查紀錄；ID 是 Identifier（識別碼）。先查看既有檔名與發現編號，避免碰撞，不覆寫原紀錄。以下是填寫契約，佔位內容不能保存成已完成審查：

```json
{
  "id": "REV-002",
  "artifact_digest": "實際審查的完整設計 digest",
  "reviewer": "實際審查者或可辨識的代理名稱",
  "session": "實際工作階段的識別",
  "model": "unknown",
  "at": "實際審查時間及時區",
  "independence": "same-session",
  "rounds": [],
  "findings": [
    {
      "id": "F-001",
      "round": "traceability",
      "case_ids": ["TC-001"],
      "rule_refs": ["AC-001"],
      "issue": "具體差異；缺規則時明說未有已確認依據",
      "evidence": "來源版本、條款與案例步驟；讀不到就記限制",
      "proposal": "交回設計端的修正建議或待人決定事項",
      "status": "open",
      "disposition": null
    }
  ],
  "limitations": []
}
```

F 取自 Finding（審查發現），TC＝Test Case（測試案例），AC＝Acceptance Criterion（驗收條件）；示例的數字是各類流水號，不代表題號或完成狀態。文件展示其他前綴時同樣提供說明，機器讀取的 ID 字串不附括號。

- independence 依實際條件填 fresh-session／human／same-session，不能靠換名稱取得獨立性。model 無法得知時保留 unknown，不編造版本。
- rounds 只加入真正完成的 traceability、executable、coverage、consistency。缺整份規格、看不到已選分母或未檢全部案例時，對應輪次不算完成。可另記 checked_case_ids 與 limitations 說明已檢部分。
- findings 必須是陣列。完成審查且沒有發現才能留空；沒看資料不能直接留空交差。Finding 的 rule_refs 沒有適用已確認規則時可為空，evidence 要明說哪個 Expected 缺依據，不創造規則編號。
- open 不代表應立即補一題產品訪談。必要決策與操作缺口一起交回設計端，讓使用者或適當責任人處理；不自行寫入 registry 或改 scope。
- disposition 只有真實人的處置才填 by、at、evidence_ref、reason。fixed 需有實際修正及確認依據；dismissed 要有駁回理由；accepted-risk 另需 residual_risk。單純記錄建議或人尚未回答時保持 open。
- 修正設計後 digest 改變，必須審查新內容；不能把舊 review 的 artifact_digest 改新或僅改 Finding 狀態冒充重審。新審查保留與前次發現的關聯。
- 完整四輪與處置紀錄只是基線前提；沒有人的明確核可，不建立 APP（Approval，核可紀錄）或 BL（Baseline，案例基線）。

## 保存與回到設計端

只新增本次審查檔，不修改 session、registry、案例、pack 或基線。已授權保存且既有專案採 Git 時，先檢查工作目錄、既有 staged 內容與本次實際 diff；只提交本次新增的審查 JSON／Markdown。不要直接執行 qa_project.py checkpoint，因其預設會納入整個 qa 與登錄來源，可能混入別人的設計變更。

可使用本機 Git 明確的檔案清單進行 add 與 commit；遇到既有 staged 變更、hook／簽章或身分問題時保留現況，說明審查檔已保存但尚未提交，不改全域設定、不停掉內容審查。已有核准的 server 同步範圍與分支可沿用並讀回驗證；本機模式不聯絡 server，僅有 remote 不能推定要 push。若推送會包含未核准的其他提交，先保留本機紀錄，交回既有保存流程處理。

沒有初始化標記或工具時，不建立 qa/ 來假裝工具可用；交付對話或使用者指定位置的審查報告，標明版本識別限制。需要納入正式基線時，由設計端把報告與對應資料接入既有專案。

交回設計端時包含實際審查版本、完成輪次、Finding 檔案與需處理項目；原焦點／題數不重設。設計端記錄人的取捨、修正案例、更新進度與閱讀網頁後，建立新的交接包。審查端不會因訪談的五題批次或明訂總上限而跳過必要的四輪檢查，也不對每五項發現增加續問選擇。設計端接回時保留原續問狀態；已選先產出或總上限已到就只列缺口，不藉修正重啟產品訪談。

工具 1.5.0 的 risk_evidence_source_ids 保留風險初評引用的觀察資料；這些資料只支持危害／可能性分析，不能取代已確認的產品 Expected。未引用的任意現況觀察仍不加入審查包。
