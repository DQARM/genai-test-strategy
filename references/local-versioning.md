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
| qa/interview.md | 原始問答、AI 解讀及更正鏈的生成視圖；真相在 registry.interactions |
| qa/risks.md | 每筆需求的風險評估狀態、危害／可能性／優先序與案例關係；由 registry 生成 |
| qa/test-design.md | 方法、覆蓋項目及探索任務的生成視圖 |
| qa/id-glossary.md | 前綴英文來源、中文意思與用途；由 render 產生 |
| qa/questions.md | 規格問題交接單，由 registry.questions 生成 |
| qa/execution-profile.json、selections/ | 選填排程及版本綁定的執行選取建議 |
| qa/source-reading.md | 來源閱讀範圍、定位摘錄、未讀與限制；由 render 產生 |
| qa/report.html | 離線閱讀網頁；來源與完整案例雙向連結，保留規則引用路徑 |
| qa/decisions/、approvals/、reviews/ | 真實決策、核可、四輪審查 |
| qa/review-packs/、baselines/ | 交接包與不可重名的案例快照 |
| qa/review-handoff.json、review-focus.md | 最近驗證交接的索引、選填的特殊審查重點；索引不能代替重新驗證 |
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
python qa/tools/qa_project.py prepare-review .
python qa/tools/qa_project.py check . --gate baseline
python qa/tools/qa_project.py baseline . --id BL-001 --approval qa/approvals/APP-001.json
python qa/tools/qa_project.py checkpoint . -m "核可 BL-001" --tag qa-baseline-BL-001
python qa/tools/qa_project.py start-run . --id RUN-001 --case TC-001 --sut-version "實際 build 或產物 hash" --environment "實際環境與工具版本"
python qa/tools/qa_project.py check-run . --id RUN-001
```

先真正建立並讀取 inputs 才傳 `--include inputs`；參數可重複指定多個明確資料夾／檔案。不含 --include 時保存 qa、專案標記、本工具新建的 .gitignore，以及 registry 明確登錄的來源與決策證據檔。其他被測原始碼與未登錄資料不會自動全部加入；讀取差異後明確納入必要檔案，以讓版本能重建。不得默默對整個未知資料夾 git add .。

初始化與第一個 checkpoint 分開完成；再次 init 沿用現有內容。工具升級及舊資料相容性統一依 [migration.md](migration.md)，功能沿革見 [CHANGELOG.md](../CHANGELOG.md)。

checkpoint 遇到既有 staged 內容會拒絕提交，不會把別人的變更混入。請讀現況、說明阻塞，保留使用者 index；可先完成文件與檢查。若 Git 缺 identity，只在這一次 commit 使用明確 automation identity，不改全域設定。hook 或簽章失敗如實回報，不能假稱保存成功。

已知私密檔名、symlink、.git、虛擬環境及 qa/evidence/raw 被略過；這不是完整的機密偵測。提交前仍需檢查檔案清單與內容，明確選擇應保存的來源／證據。大型證據可保存受控副本與 hash，但只有 hash 無法重建遺失的檔案。已有 .gitignore 不覆寫。

## 比較與復原

使用 `git log --oneline`、`git diff <old> <new> -- qa` 檢視歷史與差異。取回單檔可先用 `git show <revision>:<path>` 輸出到新的比較檔，確認後再套用。整批回復優先用保留歷史的 revert；不可自動 reset --hard、clean、force push 或刪除歷史。標籤已存在時用新版本名稱，不能移動舊基線標籤。

複製專案時要包含 `.git` 才有歷史；一般只傳目前文件的 ZIP 可能遺失它。視需要另用 `git bundle create <outside-project-path>/project-history.bundle --all` 離線備份已提交歷史；bundle 不含尚未提交檔案與被忽略的大型證據。把工作目錄、Git 歷史與必需證據都納入合適的備份；本機歷史不等於異地備份。

## 版本綁定

兩個 Skill 共用專案工具。審查包採 reference 或 portable 模式；來源、版本、重點與包完整性均相符才重用，變更建立新包。完整行為依 [review.md](review.md)。

qa/questions.md 是 registry.questions 的生成視圖；不要直接把填答寫在會被 render 覆蓋的檔案。新增 qa/execution-profile.json 與 qa/selections/ 屬執行安排，依各自指紋及原設計 digest 核對；不改原 artifacts() 對既有欄位的計算範圍。它們仍由 checkpoint 保存，但不要求因單純標籤或時程修改重新核可設計。設計、來源／風險取捨更動仍依原規則重審。

新包、manifest、回傳模板及交接索引屬審查交接產物，不改原完整設計 digest；review_focus 以獨立 hash 綁定包，變更後須新包。checkpoint 預設包含 qa，故會保存包與 portable 副本；打包前檢查來源清單及上傳範圍。大量二進位來源可採 reference 模式並維持原檔備份；可攜包不是整個專案的備份。新環境只檢包時不能重算原專案完整 digest，不能把 review_input_digest 當成原設計 digest。

artifact_digest 對應設計內容；baseline 凍結那一版內容及審查／核可；checkpoint commit 對應專案文件版本；RUN 另記 SUT build、環境與案例快照。這些不能互相冒充。

案例、規格、範圍、策略、計畫或決策證據更動會使核可 digest 過期。來源檔 hash 更動會阻止基線；先重新閱讀，更新規則與來源版本，再審查。run 的 frozen snapshots 不能改成新規格；只建立新 run。
