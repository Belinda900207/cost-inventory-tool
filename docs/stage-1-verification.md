# 第一階段驗收

驗收日期：2026-09-27。最終 `main` clean-clone 與 main-push CI 證據會在最終驗收 PR 合併後補記；以下是目前已合併主題及 PR #10 的綠燈證據。

| 驗收項 | 狀態 | 證據 |
| --- | --- | --- |
| 從乾淨 checkout 安裝與測試 | 待最終核對 | 每個 GitHub job 使用 `actions/checkout`；README 命令待 clean clone 重跑 |
| React → Vite → FastAPI → MySQL | 已通過 | PR #10 run 36322992915 browser-integration，2 passed／15.9s |
| loading／成功／DB 失敗／後端失敗 | 已通過 | browser-evidence 4 張 screenshot；DB stop 後 backend 仍運作，恢復後 healthy |
| live 與 ready 分離 | 已通過 | backend API tests；真實 DB outage 時 live 200、ready 503 |
| app user `SELECT 1`／MySQL 8.4 | 已通過 | mysql-integration log 明確輸出 MySQL 8.4 app SELECT 1 |
| 測試 DB 隔離與持久性 | 已通過 | project/port/user/db assertions；重啟前後 `@@server_uuid` 相同；不刪 volume |
| Alembic 接線、無業務 schema | 已通過 | `alembic current` 真實連線；empty revisions/metadata tests |
| Request ID／安全錯誤／結構化 log | 已通過 | backend tests 涵蓋非法/重複 ID、404/405/422/500 與秘密不洩漏 |
| Auth 邊界 | 已通過 | login/me 404；unconfigured dependency 501；無 users table／fake login |
| CI 可阻擋失敗 | 已通過 | run 36255713755 因故意 `assert False` 紅燈；移除後 run 36255812580 全綠 |
| 後端／前端／DB／browser CI | 已通過 | PR #10 run 36322992915 四 jobs 全綠 |
| `.env`／產物未追蹤、bundle 無測試秘密 | 已通過 | `scripts/check_repository.py`；PR #10 frontend log |
| 本機 Docker 驗收 | 受環境阻塞 | WSL 仍回 Docker integration 未啟用；沒有操作或刪除開發 volume |

已知 warning：FastAPI TestClient 經 Starlette 使用 `httpx` 的 deprecated 相容路徑；目前版本固定，測試持續顯示 1 warning。官方建議 `httpx2`，但不在缺少完整相容性驗證時臨時切換。

第一階段實作信心暫為 94/100。支持證據是四層 CI、真實 DB 故障／恢復、browser screenshots、精確 API/元件測試與秘密檢查；扣 6 分是本機 WSL Docker 無法驗證、final main clean clone/main push 尚待最後一張 PR。這是證據信心，不是進度百分比。
