# 本機版本控制

## 原則

兩種模式都在專案根目錄使用 `.git` 保存歷史。先詢問使用者選擇：本機模式不需帳號、Git server 或網路；server 模式另依 [git-server.md](git-server.md) 協助登入及同步。`qa_project.py` 本身沒有 remote add、fetch、pull 或 push 行為，這些由代理在 server 模式另外處理；checkpoint 成功只表示本機已保存。

既有 repo 保留設定並只提交明確檔案；專案位於別的 repo 裡時預設停止初始化，選用該根目錄，或在清楚需要獨立 repo 時明確使用 `--standalone`。需要 clone 已有內容的遠端時先建立正確工作副本再 init，不在已初始化的資料夾內另套一層 repo。

只做文件／黑箱測試也可使用。SUT build 沒有原始碼時用供應商版本＋韌體／安裝包 hash；本機 Git HEAD 只辨識測試專案，不自動代表被測產品版本。

Python 3.10+ 與 Git 是唯一執行依賴。Windows 可用 `py -3` 取代下例 python；macOS／Linux 可用 python3。命令路徑含空白時加引號。shell 不會由工具拼接執行，Git 使用參數陣列。

## 專案內容

| 路徑 | 用途 |
|---|---|
| 原有資料夾，例如 inputs/、src/ | 原始需求、介面、程式等；明確選入版本控制 |
| .qa-project.json | 初始化標記及工具版本 |
| qa/registry.json | 需求、AC、決策、問題、風險、情境與範圍 |
| qa/strategy.md、plan.md、session.md | 策略、執行安排與續作進度 |
| qa/cases/ | 結構化完整案例 |
| qa/spec.md、test-cases.md、traceability.md | 生成的人用視圖 |
| qa/risks.md | 每筆需求的風險評估狀態、危害／可能性／優先序與案例關係；由 registry 生成 |
| qa/test-design.md | 方法、覆蓋項目及探索任務的生成視圖 |
| qa/id-glossary.md | 前綴英文來源、中文意思與用途；由 render 產生 |
| qa/report.html | 離線閱讀網頁；來源與完整案例雙向連結，保留規則引用路徑 |
| qa/decisions/、approvals/、reviews/ | 真實決策、核可、四輪審查 |
| qa/review-packs/、baselines/ | 交接包與不可重名的案例快照 |
| qa/runs/、evidence/ | 實際結果與證據 |
| qa/tools/qa_project.py | 專案自帶工具，可離線使用 |

## 常用命令

第一次用技能包內的 `scripts/qa_project.py` 初始化；之後在專案根目錄：

```bash
python qa/tools/qa_project.py inventory .
python qa/tools/qa_project.py check .
python qa/tools/qa_project.py render .
python qa/tools/qa_project.py checkpoint . -m "釐清首次啟動規則並更新 AC" --include inputs
python qa/tools/qa_project.py digest .
python qa/tools/qa_project.py review-pack . --id REV-001
python qa/tools/qa_project.py check . --gate baseline
python qa/tools/qa_project.py baseline . --id BL-001 --approval qa/approvals/APP-001.json
python qa/tools/qa_project.py checkpoint . -m "核可 BL-001" --tag qa-baseline-BL-001
python qa/tools/qa_project.py start-run . --id RUN-001 --case TC-001 --sut-version "實際 build 或產物 hash" --environment "實際環境與工具版本"
python qa/tools/qa_project.py check-run . --id RUN-001
```

先真正建立並讀取 inputs 才傳 `--include inputs`；參數可重複指定多個明確資料夾／檔案。不含 --include 時保存 qa、專案標記、本工具新建的 .gitignore，以及 registry 明確登錄的來源與決策證據檔。其他被測原始碼與未登錄資料不會自動全部加入；讀取差異後明確納入必要檔案，以讓版本能重建。不得默默對整個未知資料夾 git add .。

初始化與 checkpoint 是分開動作；代理在初始化並檢查結果後應建立第一個 checkpoint。再次 init 不覆寫資料，也不升級專案內工具。工具升級先比較版本、檢查差異、保留 checkpoint 再明確替換。

工具 1.1.0 新增生成視圖的編號說明及 id-glossary.md。既有專案若仍用 1.0.0，需依上述升級流程更新 qa/tools/qa_project.py 後再 render，不能宣稱舊工具已有新功能；當輪對話仍依 identifiers.md 解釋編號。只有說明性的生成視圖改變，不修改既有 ID；若更新 registry.project.id_glossary，設計 digest 也會改變，需遵守原有審查／核可規則。

工具 1.2.0 的 render 新增 `qa/report.html`，仍只需 Python 標準函式庫；原有輸出保留。舊專案須先依上述流程將專案內工具更新至 1.2.0，再 render。新網頁是生成視圖，單純重新生成不修改 registry、案例或設計 digest；補來源、改引用或改規格則仍遵守原有變更／審查規則。說明及分享限制見 [report.md](report.md)。

checkpoint 遇到既有 staged 內容會拒絕提交，不會把別人的變更混入。請讀現況、說明阻塞，保留使用者 index；可先完成文件與檢查。若 Git 缺 identity，只在這一次 commit 使用明確 automation identity，不改全域設定。hook 或簽章失敗如實回報，不能假稱保存成功。

已知私密檔名、symlink、.git、虛擬環境及 qa/evidence/raw 被略過；這不是完整的機密偵測。提交前仍需檢查檔案清單與內容，明確選擇應保存的來源／證據。大型證據可保存受控副本與 hash，但只有 hash 無法重建遺失的檔案。已有 .gitignore 不覆寫。

工具 1.4.0 在 review-pack 加入審查 Skill 與交接協定資訊，PROMPT 指向 genai-test-review；既有 1.3.0 包仍可手動交給該 Skill。schema 1、設計 digest 與基線要求不變。兩個 Skill 共用專案的 qa/tools/qa_project.py，審查端不安裝第二份工具或重新 init。

工具 1.5.0 增加 requirement-risk-v1、直接需求關聯、嚴重度與評估狀態，以及 risks.md／HTML 風險表。舊資料可繼續 draft 檢查與 render；新基線前依 [risk-assessment.md](risk-assessment.md#檢查與舊專案) 補本輪評估及真實依據。既有工具副本需明確升級；不重建專案、不改舊基線或執行證據，填補缺欄位不代表人已核可。

## 比較與復原

工具 1.3.0 仍讀 schema 1，新增 coverage_items、charters、判準欄位及 test-design.md。升級專案內工具前保存 checkpoint、比較差異並執行檢查；重跑 init 不會替換副本或遷移資料。舊專案 draft 檢查與 render 可繼續；建立新基線前，按 [test-design.md](test-design.md#舊專案續作) 補齊當輪方法、覆蓋與斷言，設定 coverage-items-v1，對新 digest 重審核可。既有基線與執行快照不修改，不自動補人的決策。

使用 `git log --oneline`、`git diff <old> <new> -- qa` 檢視歷史與差異。取回單檔可先用 `git show <revision>:<path>` 輸出到新的比較檔，確認後再套用。整批回復優先用保留歷史的 revert；不可自動 reset --hard、clean、force push 或刪除歷史。標籤已存在時用新版本名稱，不能移動舊基線標籤。

複製專案時要包含 `.git` 才有歷史；一般只傳目前文件的 ZIP 可能遺失它。視需要另用 `git bundle create <outside-project-path>/project-history.bundle --all` 離線備份已提交歷史；bundle 不含尚未提交檔案與被忽略的大型證據。把工作目錄、Git 歷史與必需證據都納入合適的備份；本機歷史不等於異地備份。

## 版本綁定

artifact_digest 對應設計內容；baseline 凍結那一版內容及審查／核可；checkpoint commit 對應專案文件版本；RUN 另記 SUT build、環境與案例快照。這些不能互相冒充。

案例、規格、範圍、策略、計畫或決策證據更動會使核可 digest 過期。來源檔 hash 更動會阻止基線；先重新閱讀，更新規則與來源版本，再審查。run 的 frozen snapshots 不能改成新規格；只建立新 run。
