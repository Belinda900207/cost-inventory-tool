# Human-in-the-loop AI 工作方式

本專案採「GPT 協助討論需求、Codex 實作與留證、本人核對決策」的流程。

- 人：決定業務規則、認證方案、資料保留風險與是否進入下一階段；審查 PR、CI、畫面與文件。
- Codex：核對 repository 現況，分小 PR 實作，執行測試，保護既有資料，記錄失敗與限制，不自行補業務規則。
- Git／GitHub：保存 diff、commit、PR、reviewable evidence 與可重現 CI，不把聊天內容當唯一紀錄。

使用 AI 時不得貼 token、`.env` 值、真實密碼、個資或 production 資料。命令輸出若可能含秘密，先改成只顯示檔名、狀態或安全摘要。AI 提議的 migration、auth、財務或庫存規則必須由本人確認；第一階段因此保持空 schema 與 auth 介面。

驗收時以實際執行結果為準：測試數、warning、CI run、artifact 與可重建命令。信心值描述證據完整度，不等同完成百分比；必要項沒通過時要標示階段仍進行中。
