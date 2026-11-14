# 來源閱讀紀錄

## 編號說明

ID＝Identifier（識別碼）。以下為本專案採用的前綴含義；不是通用強制標準。
純數字後綴如 01／001 是該類別的流水號，不代表優先度、版本、確認狀態或測試結果。
非數字後綴是專案標籤，具體含義須依來源記錄確認；RISK／RUN 本身是英文單字。

| 前綴 | 英文來源 | 中文意思 | 用途 |
|---|---|---|---|
| SRC | Source | 資料來源 | 追蹤文件、操作指南或其他依據 |
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
    "seq": 2,
    "read_scope": [
      "inputs/spec.md 第 1 行（全文）"
    ],
    "unread_scope": [],
    "limitations": [
      "原文沒有重啟後輸出規則，不可推導重啟 Expected。"
    ]
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
    },
    {
      "source_sha256": "f574cfbae3eedc1dc70434c467a38a47a2b550511edfdef06c16521d9c0ba691",
      "status": "scoped",
      "depth": "content",
      "purpose": "接回既有審查發現，補明確初態讀值並保留重啟規則缺口。",
      "method": "以 Python Path.read_text 實際讀取 UTF-8 原檔全文，核對第 1 行及現有審查與案例。",
      "read_scope": [
        "inputs/spec.md 第 1 行（全文）"
      ],
      "unread_scope": [],
      "findings": [
        {
          "locator": "inputs/spec.md:1",
          "type": "quote",
          "text": "Synthetic test rule: after evaluate, output ON.\n",
          "interpretation": "本輪只沿用 evaluate 後 ON 的既有應然規則；原文沒有重啟後輸出定義。"
        }
      ],
      "limitations": [
        "原文沒有重啟後輸出規則，不可推導重啟 Expected。"
      ],
      "evidence_refs": [],
      "read_at": null,
      "reader": "ChatGPT",
      "seq": 2,
      "recorded_at": "2026-11-14T13:08:17+00:00"
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
    "seq": 2,
    "read_scope": [
      "inputs/harness.md 第 1 行（全文）"
    ],
    "unread_scope": [],
    "limitations": [
      "簡短文件僅列操作名稱及隔離條件，沒有產品命令或重啟行為；本輪不補造 API、命令或重啟判準。"
    ]
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
    },
    {
      "source_sha256": "6050ea2d883af7e763867cd2cc9320f8347986265482bc05f42bc28ee325c140",
      "status": "scoped",
      "depth": "content",
      "purpose": "接回既有審查發現，補明確初態讀值並保留重啟規則缺口。",
      "method": "以 Python Path.read_text 實際讀取 UTF-8 原檔全文，核對第 1 行及現有審查與案例。",
      "read_scope": [
        "inputs/harness.md 第 1 行（全文）"
      ],
      "unread_scope": [],
      "findings": [
        {
          "locator": "inputs/harness.md:1",
          "type": "quote",
          "text": "Synthetic harness: reset, evaluate, inspect output; isolated state.\n",
          "interpretation": "原文列出 reset、evaluate、inspect output 與隔離狀態；本輪用該觀測介面補初態讀值。OFF 初態取自既有案例及本輪明確處置，並非原文另有定義 reset／重啟結果。"
        }
      ],
      "limitations": [
        "簡短文件僅列操作名稱及隔離條件，沒有產品命令或重啟行為；本輪不補造 API、命令或重啟判準。"
      ],
      "evidence_refs": [],
      "read_at": null,
      "reader": "ChatGPT",
      "seq": 2,
      "recorded_at": "2026-11-14T13:08:17+00:00"
    }
  ]
}
```

