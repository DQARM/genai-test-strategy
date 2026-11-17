# 審查交接

交接編號：REV-002（REV 取自 Review，數字為審查類流水號）。
完整設計版本：c7125643c1e9517cd7058a7e52de0712b137216425550a9c1bbda9ff1e0832fe

同一工作區：請在新工作階段審查專案 "/workspace/scratch/258261bef5fc/phase-update/run-01/workspaces/case-10/project"，讀取 "/workspace/scratch/258261bef5fc/phase-update/run-01/workspaces/case-10/project/qa/review-packs/REV-002/PROMPT.md"，依包內四輪準則執行，只新增審查結果。

另一個平台／模型：此包只含來源清單，尚未複製原檔。請先由設計端 prepare-review --portable 產生可攜包，再提供給另一個環境；只貼本機路徑不保證可讀。

回傳：依 REVIEW_TEMPLATE.json 建立新的結果 JSON 與摘要，保留 artifact_digest／review_pack_id；不要修改模板、輸入、原設計或既有審查。
不同模型仍須新對話、實際讀原文；無法確認獨立性就如實標示。尚未執行產品測試或取得人工核可。
