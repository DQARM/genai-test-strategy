# 不同專案的案例設計示意

## 閱讀條件

只在使用者需要示例時選用相關小節。下列各專案、規則與介面均為獨立的教學假設；不會在 init 時建立，也不能直接寫入使用者專案的 registry。實際資料中沒有相應規格或介面時，須釐清或標記 blocked。

共用的完整度要求見 templates.md；使用任何實際案例都要填本專案自己的來源 ID、AC、風險、資料、版本、操作與證據。

以下尚未綁定真實專案的範例均屬草稿。尤其帳號／fixture 建立與清理、版本辨識、完成事件等若只有概述，必須補成實際命令或操作路徑及其引用文件；不能直接把範例標成 ready。

## A. Web 操作：取消編輯後保留原值

僅對這個教學專案假設已確認：

- 規則 AC-WEB-CANCEL：編輯個人顯示名稱後按「取消」，不得保存此次修改；重新開啟設定頁須顯示原值。
- 介面文件：測試帳號的「帳戶設定」頁有「顯示名稱」「儲存」「取消」。可建立專用帳號並設定已保存初值；重新進入設定頁會讀取保存值，不使用前頁未儲存的暫存內容。
- 本輪驗證 UI 與文件所述的重載行為，不宣稱有直接查詢資料庫的證據。

案例結構示意 TC-WEB-CANCEL：

1. 環境：記錄實際 Web build、瀏覽器版本、測試環境及專用帳號。
2. 初態：建立本案專用帳號，將顯示名稱存成 `Sample-A`。離開再進入設定頁，確認顯示 `Sample-A`。
3. 操作：將輸入欄改為 `Sample-B`；尚未按儲存，按「取消」。
4. 操作：依介面文件重新開啟設定頁；等待文件定義的頁面載入完成事件，不自訂數值逾時門檻。
5. 判定：在重新載入完成後讀取顯示名稱。Expected 是 `Sample-A`，依據 AC-WEB-CANCEL；記錄實際值。若介面不能確定已重新載入則記無法判定。
6. 證據：保留已保存初態、修改未儲存、取消及重新載入結果的連續操作記錄，包含 build、帳號標識與時間。
7. 清理：依已確認的測試帳號管理程序移除專用帳號或恢復本案 fixture；保留證據。下次重建初態，不依賴本次結果。

未確認事項的處理：若專案只說「可以取消」而沒說取消哪些狀態，先問取消的效果；不能套用上面的保存與重載規則。

## B. API 服務：已存在項目的讀取契約

僅對這個教學專案假設已確認：

- 規則 AC-API-READ：取得已存在的項目時，回覆狀態 200，JSON 的 `id` 與 `name` 對應該項目。
- 介面文件：隔離服務為 `http://127.0.0.1:8080`；使用 `GET /items/item-a`。該測試服務不需憑證；已提供的 fixture 管理程序可獨立建立、確認及移除 `item-a`，name 為 `Example-A`。回覆完成即可判讀；其他欄位未納入本輪。

案例結構示意 TC-API-READ：

1. 環境：記錄實際服務 build、curl 版本與隔離服務配置；確認服務確實是上述本機測試實例。
2. 初態：依本案 fixture 程序建立 `item-a`，確認其名稱為 `Example-A`。無法獨立建立或確認 fixture 時記 blocked。
3. 操作：在可連接該隔離服務的終端執行 `curl --silent --show-error --include http://127.0.0.1:8080/items/item-a`，保存命令、時間、退出碼、完整 header／body 與 stderr。
4. 判定：同一個 request 完成後，確認回應狀態為 200，body 可解析為 JSON，`id` 等於 `item-a`、`name` 等於 `Example-A`。每項 Expected 均對應 AC-API-READ；curl 的退出碼不能代替 HTTP 狀態或 body 判斷。
5. 失敗／無法判定：前提與連線有效但契約欄位不符記 FAIL；環境或 fixture 不成立記 BLOCKED／INCONCLUSIVE。記錄實際觀察，不用預期值補 Actual。
6. 清理：依 fixture 程序移除 `item-a`，核對清理結果並保留原始回覆。下一次重建，不依賴其他 TC。

真實專案使用自己的 base URL、認證方式、endpoint、欄位與 fixture；本例不提供通用的 HTTP 狀態或資料模型預設。

## C. 資料匯入：有錯誤列時的處理方式

原始描述只有「把 CSV 匯入資料庫」時，先問最有影響的分歧，例如單列錯誤時整批拒絕或只跳過該列。合法欄位、唯一性、空值、交易範圍及操作介面都依專案資料確認。

只有在這個教學專案已明確決定「整批拒絕、保留匯入前資料、指出錯誤列」，並提供可用介面後，才可形成案例：

1. 依實際 fixture 操作建立本案獨立資料範圍，取得匯入前可核對的資料快照。
2. 準備一份符合已確認格式的 CSV，包含一筆合法列與一筆違反已確認欄位規則的列；明列實際內容、列號及違反的規則。
3. 使用已確認的 UI／API／CLI 匯入，保存輸入檔、版本、提交及完成事件。
4. 在約定完成時點核對錯誤列回饋與匯入後資料快照，依已確認 AC 判斷整批未寫入。
5. 保存結果與前後差異，清理本案 fixture 並保留證據。

本段刻意沒有虛構某個產品的匯入命令或資料庫查詢。若實際資料未提供第 1、3、4 步的操作映射，這只是待補足的案例草稿，必須標 blocked；補齊真實方式後才能宣稱完整可執行。

## D. 完整演練：項目數量門檻告警

本節附可在本機操作的 [demo_counter.py](../scripts/demo_counter.py)，只有 Python 標準函式庫、不連網、不控制設備。它是教學受測程式，不是使用者產品；以下規則及取捨均為教學前提，不代表任何真實專案的核可。

編號圖例：SRC＝Source（來源）；REQ＝Requirement（需求）；AC＝Acceptance Criterion（驗收條件）；DEC＝Decision（決策）；RISK＝Risk（風險）；COV 取自 Coverage（覆蓋項目）；TC＝Test Case（案例）。DEMO 為本節教學標籤，其他數字是流水號；49／50 在案例名稱中表示輸入值。

### 已知條件與依據

| 項目 | 本節已給定內容 | 依據 |
|---|---|---|
| 需求 REQ-DEMO-01 | 單次評估輸入的項目數，輸出是否告警 | SRC-DEMO-RULE：本節規則文字，revision 1 |
| 驗收 AC-DEMO-01 | count 為 0～100 的整數、單位「筆」、步距 1；count ≥50 時 alarm=true，count <50 時 alarm=false；每次呼叫獨立，回傳後判定、布林值須完全相等 | SRC-DEMO-RULE；不是從程式輸出反推 |
| 操作 | `--count` 接收數值、`--record` 指定新 JSON 檔；不覆寫既有檔案。每次命令是新程序、沒有持久控制狀態 | SRC-DEMO-OPS：腳本的 `--help` 及本節操作說明；script 版本 counter-demo 1.0，另記實際 hash |
| 風險 RISK-DEMO-01 | 門檻等號寫錯，造成應告警的 50 沒有告警 | 由已給定規則分析 |
| 範圍 DEC-DEMO-01 | 本次只選告警交界的二值邊界，人工輸入命令與判讀；其他資料格式、上下限端點與跨次行為不列本輪驗收 | 教學取捨，未測部分列剩餘風險 |
| 未決 | 不合法資料的產品錯誤回應未定義；不從 argparse 的現行訊息建立 Expected | 待釐清或探索 |

### 由方法列出項目

規則有有序整數及明確門檻，選 `boundary-2`（二值邊界分析）。交界的兩個邊界值是 49、50；去重後只需這兩個輸入。若選三值邊界，則為 48、49、50、51，不把 49、50、51 誤稱完整三值集合。

| COV | AC | 方法／具體項目 | 選取理由 | 承接案例 |
|---|---|---|---|---|
| COV-DEMO-01 | AC-DEMO-01 | boundary-2；未告警分區的上邊界，count=49，預期 false | keep；驗證門檻前一值 | TC-DEMO-49 |
| COV-DEMO-02 | AC-DEMO-01 | boundary-2；告警分區的下邊界，count=50，預期 true | keep；驗證包含等於 | TC-DEMO-50 |

這兩項只承接所選的告警交界，不宣稱整個輸入域、所有異常或真實產品已被完整測試。增加情境時先沿用或更新範圍取捨。

記錄對應示意：

```json
{
  "coverage_ids": ["COV-DEMO-02"],
  "checks": [{
    "expected": "alarm 為布林值 true",
    "rule_refs": ["AC-DEMO-01"],
    "coverage_ids": ["COV-DEMO-02"]
  }]
}
```

這是欄位片段；coverage_ids 放案例頂層，checks 放觀測步驟內。所引用記錄須先存在，不是可獨立匯入的 registry。

### TC-DEMO-49：門檻前一值不告警

- revision 1；層級 unit；執行方式 manual。目的：檢查 COV-DEMO-01；判準 AC-DEMO-01、風險 RISK-DEMO-01。這是教學案例設計，Actual 與結果尚未填寫。
- 環境：Python 3.10+ 的本機終端；複製腳本至一個全新練習資料夾，在該資料夾開終端。Windows 若沒有 python 別名，以 `py -3` 替代每個命令的 python；Linux 可用 python3。
- 獨立前置：執行 `python --version` 與 `python demo_counter.py --version`，記下實際版本，確認後者為 counter-demo 1.0。執行 `python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('demo_counter.py').read_bytes()).hexdigest())"` 保存 hash。確認該資料夾沒有 demo-49.json；有舊紀錄就換新練習資料夾，不刪改舊證據。無其他初態，每次都是新程序。
- 測試資料：count=49，單位筆，依 AC-DEMO-01 的步距及 COV-DEMO-01；不需要外部帳號、資料庫或設備。

| 步驟 | 操作／輸入 | 觀察與時機 | Expected／依據 | 證據 |
|---|---|---|---|---|
| 1 | 執行 `python demo_counter.py --count 49 --record demo-49.json` | 命令返回後，開啟生成的 JSON；核對 fixture_version、count 與本次輸入 | 版本與 count 是本案環境／輸入確認，不代替告警判準 | 命令、終端輸出／錯誤、demo-49.json |
| 2 | 在同一 JSON 讀取 alarm 欄位 | 步驟 1 返回後立即判讀本次檔案 | alarm 為布林值 false；AC-DEMO-01、COV-DEMO-01 | 記錄實際值、時間及檔案 hash |

- 判定：前置與輸入有效，alarm=false 才符合本案；有效執行卻為 true 是不符合；工具不可用、檔案不屬於本次或無法取得觀測時記 BLOCKED／INCONCLUSIVE，不把預期填成實際。
- 清理：確認命令已返回、沒有持續程序；保留本次 JSON 與版本證據。程式沒有背景服務或持久控制狀態，無須重置產品。下次在新的練習資料夾重新複製腳本、驗版本與 hash；不依賴 TC-DEMO-50。

### TC-DEMO-50：等於門檻會告警

- revision 1；層級 unit；執行方式 manual。目的：檢查 COV-DEMO-02 的等號；判準 AC-DEMO-01、風險 RISK-DEMO-01。Actual 與結果尚未填寫。
- 環境：本機 Python 3.10+、獨立的全新練習資料夾及腳本副本。自行執行 `python --version`、`python demo_counter.py --version` 與 `python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('demo_counter.py').read_bytes()).hexdigest())"`；確認 counter-demo 1.0 並記實際 hash，不沿用前一案例結果。
- 前置：確認本資料夾沒有 demo-50.json；有舊檔即換新資料夾。每次新程序、無持久初態。測試資料 count=50、單位筆，來源 AC-DEMO-01 與 COV-DEMO-02。

| 步驟 | 操作／輸入 | 觀察與時機 | Expected／依據 | 證據 |
|---|---|---|---|---|
| 1 | 執行 `python demo_counter.py --count 50 --record demo-50.json` | 命令返回後開啟本次 JSON，核對 fixture_version 及 count=50 | 版本與 count 是環境／輸入確認 | 命令、終端輸出／錯誤、demo-50.json |
| 2 | 讀取本次 JSON 的 alarm | 步驟 1 返回後判讀 | alarm 為布林值 true；AC-DEMO-01、COV-DEMO-02 | 實際值、時間及檔案 hash |

- 判定：有效前置／執行且 alarm=true 才符合；有效執行卻為 false 是不符合；版本、輸入或觀測無法確認時記 BLOCKED／INCONCLUSIVE。
- 清理：確認命令已結束、保留本次證據；沒有背景服務或持久控制狀態。再次執行另用新資料夾與新紀錄，不依賴其他 TC。

這裡的共同命令是操作文件，不是另一案例的執行結果；兩案都自行完成準備。執行人依實際輸出填 Actual，文件中的 Expected 不自動變成 PASS。即使示範全部符合，也不能據此判定使用者的產品。

### 同一範圍的探索與審查

若想了解未定義的輸入錯誤回應，可另擬有時間上限的探索任務，沿用腳本已知的輸入介面，記下實際命令、錯誤與證據；先不把某個錯誤訊息列為產品判準。這份任務不填補上述正式案例的 COV，也不擴張已選驗收範圍。

四輪審查核對規則來源、兩案的獨立步驟、49／50 的實際承接與一致性。工具可發現 COV-DEMO-02 沒有任何已選案例斷言，卻不能只看文字發現有人把 60 錯標成門檻 50；後者需要語意審查。正式專案仍需真實審查與人的核可，不能把本節的教學 DEC 當成核可記錄。

## 從範例回到使用者專案

選擇思考方式，不複製範例規則。每次輸出都能回答：這個操作在哪份本專案文件中？這個 Expected 由哪個已確認 AC 支持？這份證據能證明哪一層承諾？答不出來就列缺口。
