# 來源閱讀紀錄

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| AC | Acceptance Criterion | 驗收條件 | 定義可觀測且可判定的產品條件 |
| SRC | Source | 資料來源 | 追蹤文件、操作指南或其他依據 |
| TC | Test Case | 測試案例 | 保存完整前置、步驟、判準與證據要求 |
| UTF | 待確認 | 待確認 | 請確認本專案定義，不猜測英文來源 |

由 registry.sources 產生。閱讀狀態、來源採納與本輪用途分開；登錄或檔案指紋不證明已讀。

閱讀紀錄序號與摘錄序號皆從 1 起算，僅在該來源／紀錄內定位；不是版本、優先度或核可。

## SRC-SPEC

閱讀：已讀指定範圍（依紀錄）；採納：confirmed；用途：normative

```json
{
  "reading_state": {
    "status": "scoped",
    "label": "已讀指定範圍（依紀錄）",
    "seq": 1,
    "read_scope": [
      "whole synthetic file"
    ],
    "unread_scope": [],
    "limitations": []
  },
  "readings": [
    {
      "seq": 1,
      "source_sha256": "f574cfbae3eedc1dc70434c467a38a47a2b550511edfdef06c16521d9c0ba691",
      "status": "scoped",
      "depth": "content",
      "purpose": "Synthetic tool regression",
      "method": "Read synthetic UTF-8 fixture",
      "read_scope": [
        "whole synthetic file"
      ],
      "unread_scope": [],
      "limitations": [],
      "findings": [
        {
          "locator": "whole file",
          "type": "quote",
          "text": "Synthetic test rule: after evaluate, output ON.\n"
        }
      ],
      "evidence_refs": [],
      "read_at": null,
      "recorded_at": "2026-11-13T00:00:00Z"
    }
  ]
}
```

## SRC-HARNESS

閱讀：已讀指定範圍（依紀錄）；採納：confirmed；用途：harness

```json
{
  "reading_state": {
    "status": "scoped",
    "label": "已讀指定範圍（依紀錄）",
    "seq": 1,
    "read_scope": [
      "whole synthetic file"
    ],
    "unread_scope": [],
    "limitations": []
  },
  "readings": [
    {
      "seq": 1,
      "source_sha256": "6050ea2d883af7e763867cd2cc9320f8347986265482bc05f42bc28ee325c140",
      "status": "scoped",
      "depth": "content",
      "purpose": "Synthetic tool regression",
      "method": "Read synthetic UTF-8 fixture",
      "read_scope": [
        "whole synthetic file"
      ],
      "unread_scope": [],
      "limitations": [],
      "findings": [
        {
          "locator": "whole file",
          "type": "quote",
          "text": "Synthetic harness: reset, evaluate, inspect output; isolated state.\n"
        }
      ],
      "evidence_refs": [],
      "read_at": null,
      "recorded_at": "2026-11-13T00:00:00Z"
    }
  ]
}
```

## SRC-001

閱讀：已讀指定範圍（依紀錄）；採納：confirmed；用途：experience

```json
{
  "reading_state": {
    "status": "scoped",
    "label": "已讀指定範圍（依紀錄）",
    "seq": 1,
    "read_scope": [
      "執行基本資料：/id, /status, /case_id, /artifact_digest, /sut_version, /environment, /operator, /started_at, /finished_at, /steps, /notes",
      "/case_snapshot 的初態、步驟、斷言、判定、清理及隔離要求；已核對快照與接手時案例／registry 一致"
    ],
    "unread_scope": [
      "未將與本輪失效分類無關的重複設計快照欄位逐欄重新引用。"
    ],
    "limitations": [
      "合成資料；無本輪獨立重現、根因分析或修復後結果。",
      "未提供所有執行次數、現場暴露量或完整觀測期間，不可估發生機率。",
      "回報沒有另外提供完整初態／清理紀錄、產物 hash 與實際依賴工具版本；保留證據完整性限制。"
    ]
  },
  "readings": [
    {
      "read_scope": [
        "執行基本資料：/id, /status, /case_id, /artifact_digest, /sut_version, /environment, /operator, /started_at, /finished_at, /steps, /notes",
        "/case_snapshot 的初態、步驟、斷言、判定、清理及隔離要求；已核對快照與接手時案例／registry 一致"
      ],
      "unread_scope": [
        "未將與本輪失效分類無關的重複設計快照欄位逐欄重新引用。"
      ],
      "findings": [
        {
          "locator": "/status; /case_id; /sut_version; /environment; /operator; /started_at; /finished_at; /steps/0",
          "type": "paraphrase",
          "text": "回報者 synthetic-tester 在 synthetic-lab 對 fixture-build-7 執行 TC-001；區間 2026-11-14T10:00:00+08:00 至 10:00:02+08:00。步驟 1 與整體記為 FAIL，步驟時間 10:00:01+08:00。",
          "interpretation": "這是使用者確認來源的合成執行回報；不是本輪 AI 操作產品或獨立重現。"
        },
        {
          "locator": "/steps/0/actual",
          "type": "quote",
          "text": "Evaluate returned but output stayed OFF",
          "interpretation": "支持 evaluate 返回但輸出未從 OFF 轉成 ON 的既有失效線索；根因與可重現頻率未提供。"
        },
        {
          "locator": "/steps/0/evidence/0",
          "type": "paraphrase",
          "text": "證據為 qa/evidence/failure.log；登錄 sha256 為 077d6fb7d0c5ffb3f1fcea0048d592131a4c6d1d9e1043c51667b1293d53793c。",
          "interpretation": "已讀日誌第 1 行並檢查實檔指紋相符；hash 只證明版本一致，不證明產品真實性。"
        },
        {
          "locator": "/case_snapshot/steps/0/checks/0; /case_snapshot/preconditions/0",
          "type": "paraphrase",
          "text": "凍結案例從 OFF 初態 evaluate once，預期 output ON，引用 AC-001；先 reset fixture to OFF 並 read output OFF。",
          "interpretation": "Expected 仍以原本規格與已確認驗收條件為依據，不從本次日誌 expected=ON 推導新規則。"
        }
      ],
      "limitations": [
        "合成資料；無本輪獨立重現、根因分析或修復後結果。",
        "未提供所有執行次數、現場暴露量或完整觀測期間，不可估發生機率。",
        "回報沒有另外提供完整初態／清理紀錄、產物 hash 與實際依賴工具版本；保留證據完整性限制。"
      ],
      "source_sha256": "7c1bc0f9a10f3e9657e449a65c82a7461d1d291737bb7367f4bedc2475314042",
      "status": "scoped",
      "depth": "content",
      "purpose": "接回合成測試回報，區分產品失效線索與環境阻塞，重評既有輸出控制風險。",
      "method": "以 Python 讀取 JSON 指定欄位及 UTF-8 日誌正文；以專案 check-run 核對快照與證據指紋。",
      "evidence_refs": [],
      "read_at": null,
      "reader": "Codex",
      "seq": 1,
      "recorded_at": "2026-11-14T13:08:59+00:00"
    }
  ]
}
```

## SRC-002

閱讀：已讀指定範圍（依紀錄）；採納：confirmed；用途：experience

```json
{
  "reading_state": {
    "status": "scoped",
    "label": "已讀指定範圍（依紀錄）",
    "seq": 1,
    "read_scope": [
      "/id, /status, /case_id, /artifact_digest, /sut_version, /environment, /operator, /started_at, /finished_at, /steps, /notes",
      "已核對案例／registry 凍結快照與接手時版本一致"
    ],
    "unread_scope": [
      "未將與本輪環境阻塞分類無關的重複設計快照欄位逐欄重新引用。"
    ],
    "limitations": [
      "合成回報且未附獨立 evidence；不推定已重現供電問題。",
      "evaluate 未執行，沒有產品輸出觀察，不納入產品失敗次數。",
      "本輪不恢復供電、不操作產品、不新增執行結果。"
    ]
  },
  "readings": [
    {
      "read_scope": [
        "/id, /status, /case_id, /artifact_digest, /sut_version, /environment, /operator, /started_at, /finished_at, /steps, /notes",
        "已核對案例／registry 凍結快照與接手時版本一致"
      ],
      "unread_scope": [
        "未將與本輪環境阻塞分類無關的重複設計快照欄位逐欄重新引用。"
      ],
      "findings": [
        {
          "locator": "/status; /case_id; /sut_version; /environment; /operator; /started_at; /finished_at; /steps/0",
          "type": "paraphrase",
          "text": "回報者 synthetic-tester 在 synthetic-lab 對 fixture-build-7 的 TC-001 記為 BLOCKED；區間 2026-11-14T10:10:00+08:00 至 10:10:01+08:00。步驟 1 同為 BLOCKED，evidence 為空陣列。",
          "interpretation": "保留環境／操作阻塞分類；evaluate 未執行，不能算產品失敗、成功或修復後重跑證據。"
        },
        {
          "locator": "/steps/0/actual",
          "type": "quote",
          "text": "Fixture power unavailable; evaluate not performed",
          "interpretation": "只支持供電不可用的回報線索。未附獨立供電診斷證據，供電問題根因仍待確認。"
        }
      ],
      "limitations": [
        "合成回報且未附獨立 evidence；不推定已重現供電問題。",
        "evaluate 未執行，沒有產品輸出觀察，不納入產品失敗次數。",
        "本輪不恢復供電、不操作產品、不新增執行結果。"
      ],
      "source_sha256": "105eb1557b22496fb0749908ccfc3177d788ab3ba41e6b1e1d344d6116ccc596",
      "status": "scoped",
      "depth": "content",
      "purpose": "接回合成測試回報，區分產品失效線索與環境阻塞，重評既有輸出控制風險。",
      "method": "以 Python 讀取 JSON 指定欄位及 UTF-8 日誌正文；以專案 check-run 核對快照與證據指紋。",
      "evidence_refs": [],
      "read_at": null,
      "reader": "Codex",
      "seq": 1,
      "recorded_at": "2026-11-14T13:08:59+00:00"
    }
  ]
}
```

## SRC-003

閱讀：已讀指定範圍（依紀錄）；採納：confirmed；用途：experience

```json
{
  "reading_state": {
    "status": "scoped",
    "label": "已讀指定範圍（依紀錄）",
    "seq": 1,
    "read_scope": [
      "第 1 行（全文）"
    ],
    "unread_scope": [],
    "limitations": [
      "單一合成日誌，沒有總執行數、暴露量或長期觀測資料。",
      "未記 build、環境及執行人；這些條件由第一份回報綁定，不能僅由日誌證明。",
      "沒有完整初態建立、隔離、清理與修復後驗證紀錄。"
    ]
  },
  "readings": [
    {
      "read_scope": [
        "第 1 行（全文）"
      ],
      "unread_scope": [],
      "findings": [
        {
          "locator": "第 1 行",
          "type": "quote",
          "text": "2026-11-14T10:00:01+08:00 initial=OFF evaluate_returned=true observed=OFF expected=ON",
          "interpretation": "與第一份回報步驟 1 的時間及 Actual 一致，支持在該次合成紀錄下 evaluate 返回而仍觀察到 OFF。expected=ON 只是日誌欄位，產品應然值仍引用原規格。"
        }
      ],
      "limitations": [
        "單一合成日誌，沒有總執行數、暴露量或長期觀測資料。",
        "未記 build、環境及執行人；這些條件由第一份回報綁定，不能僅由日誌證明。",
        "沒有完整初態建立、隔離、清理與修復後驗證紀錄。"
      ],
      "source_sha256": "077d6fb7d0c5ffb3f1fcea0048d592131a4c6d1d9e1043c51667b1293d53793c",
      "status": "scoped",
      "depth": "content",
      "purpose": "接回合成測試回報，區分產品失效線索與環境阻塞，重評既有輸出控制風險。",
      "method": "以 Python 讀取 JSON 指定欄位及 UTF-8 日誌正文；以專案 check-run 核對快照與證據指紋。",
      "evidence_refs": [],
      "read_at": null,
      "reader": "Codex",
      "seq": 1,
      "recorded_at": "2026-11-14T13:08:59+00:00"
    }
  ]
}
```

