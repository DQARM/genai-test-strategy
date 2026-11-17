本包可交給另一個模型的新對話，不需要安裝 Skill 或原設計對話。先讀 REVIEW_GUIDE.md、manifest.json、packet.json，再回到原文件核對。
特殊審查重點保存在 packet.review_focus；不能忽略，也不能假稱未提供的額外重點已檢查。
portable 包依 manifest.inputs.bundle_path 讀來源；reference 包需要原專案。使用 verify_pack.py check-review-pack <本包資料夾>；reference 包另加 --project <可讀專案>。
本包曾在建立時檢查；接手仍要核對目前可讀檔案。無 Python 時人工核對並記工具驗證限制，不假稱已執行。
若已安裝 genai-test-review 可使用它；否則直接按 REVIEW_GUIDE.md 執行。依 REVIEW_TEMPLATE.json 回傳新的 JSON 與摘要，勿改輸入、模板或既有結果。
