# 儲存庫協作規則

本文件只適用於 `DQARM/genai-test-strategy` 的維護，不替使用這個 Skill 的其他專案指定分支或版控方式。

## 分支與 Pull Request

- `dev` 是日常開發與推送的目標分支。開始修改前先讀取遠端最新狀態，保留既有工作。
- 後續 Skill、文件與工具的變更一律推送至 `dev`，不得直接推送或以檔案 API 修改 `main`。
- `main` 的變更必須經過 PR（Pull Request，合併請求）；一般方向為 `dev → main`。
- 建立 PR 時明確指定 `head=dev`、`base=main`。預設分支改為 `dev` 後，不能依賴 GitHub 自動選到正確的 PR 目標。
- 已有相同方向且涵蓋本次工作的開啟中 PR 時，更新原 PR，避免重複建立。
- PR 說明應包含具體變更、驗證結果與已知限制；遵守儲存庫實際啟用的審查及合併條件。單純要求推送變更不代表要求立即合併 PR。
- 不使用 force push、不改寫 `main` 歷史，不為了完成推送而略過 PR 流程。
- 記錄並區分「已推送 dev」「已開 PR」「已合併 main」；沒有讀回確認就不宣稱完成。

## 驗證與範圍

- 按變更內容執行適當檢查。修改工具時可使用：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_qa_project.py'`。
- 單純文件或分支設定更新，不需要建立 CI/CD；確認內容、連結與遠端狀態即可。
- 保留通用產品適用性、手動測試、需求追溯與既有教學文件；不要把此儲存庫的分支規則加入每位 Skill 使用者的專案預設。
- 本文件是協作指引，不等於 GitHub 已強制啟用分支保護。需要伺服器強制限制時，另確認方案、權限與實際啟用的設定。
