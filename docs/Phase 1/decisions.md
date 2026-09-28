# 第一階段決策紀錄

| 決策 | 原因 | 邊界／後續 |
| --- | --- | --- |
| 保留 Oxlint，另跑 `tsc -b` | 專案已使用 Oxlint；重複加入 ESLint 無法增加相同比例的價值 | 若未來需要只有 ESLint plugin 提供的規則，再以獨立 ADR 評估 |
| `/health` 保持相容，新增 live/ready | 舊合約已有精確測試；運維需區分 process 與 DB | 新 client 使用 `/health/live`、`/health/ready` |
| Request ID 嚴格白名單 | 避免 header injection 與無界 log 欄位 | 非法、重複、過長 ID 一律換成 UUID |
| Log 不記輸入與原始例外 | 密碼、DB URL 或個資可能存在於 query/body/error | 除錯以 request ID 對應受控內部觀測；本階段不輸出 traceback |
| MySQL healthcheck 用 app user + option file | `-pPASSWORD` 會暴露在 argv；root ping 也不能證明 app 權限 | option file 權限 0600、每次檢查後清除，只執行 `SELECT 1` |
| 測試 DB 與開發 DB 完全分離 | 故障測試會 stop/restart DB，不能危及使用者資料 | 固定 project/name/port assertions，不刪 volume |
| Alembic 直接使用應用 URL object | 避免 ini 明文與 `%` interpolation 問題 | 無 `create_all()`；第一階段無 revision |
| Auth fail closed、只留介面 | 身分來源、session、角色尚未由本人決定 | 詳見 auth-contract.md；不採假登入或 JWT/localStorage 預設 |
| CI 先做故障演練 | PR #1 沒有 checks，需證明門檻真的能擋失敗 | run 36255713755 預期紅燈；修正版後才合併 |
| Browser artifact 保存 14 天 | 讓狀態畫面可由 CI 審查，同時控制儲存成本 | 長期證據以 run URL、測試摘要和文件保存 |

Python 3.14.4、Node 24.21.0、Ruff 0.16.8 與前端 lockfile 在 CI 固定。MySQL 使用 `mysql:8.4`，會取得 8.4 系列安全修補；若需要完全 immutable image，第二階段再固定 digest 並建立更新流程。
