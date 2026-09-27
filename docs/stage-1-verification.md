# 第一階段驗收

驗收日期：2026-09-27。驗收基準是遠端 `main` commit `22e87b54c8d24880d7f9c38ddc671c7c928ffc05`，並以獨立 clean clone、本機隔離 MySQL 與 main push CI 交叉驗證。

| 驗收項 | 狀態 | 證據 |
| --- | --- | --- |
| 從乾淨 clone 安裝與測試 | 已通過 | `/tmp/cost-inventory-clean-zI2ddv/repo` 從遠端 main clone；Python/npm 全新安裝後 backend 18 passed、frontend 7 passed、build/品質檢查全過 |
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
| 本機 Docker 驗收 | 已通過（使用 `docker.exe`） | Docker Desktop server 29.8.0；隔離 MySQL integration 1 passed／19.93s；完成 restart、live 200、ready 503、recovery，最後只 stop 且保留 volume |
| 合併後 main CI | 已通過 | push run 36323469957，commit `22e87b5` 的四個 jobs 全綠 |

已知 warning：FastAPI TestClient 經 Starlette 使用 `httpx` 的 deprecated 相容路徑；目前版本固定，測試持續顯示 1 warning。官方建議 `httpx2`，但不在缺少完整相容性驗證時臨時切換。

第一階段實作信心為 98/100。支持證據是 clean clone、四層 PR/main CI、本機與 CI 各自完成真實 DB 故障／恢復、browser screenshots、精確 API/元件測試與秘密檢查；扣 2 分是原生 WSL `docker` integration symlink 仍失效，本機需用 PATH 上的 `docker.exe`，以及已知 Starlette/httpx deprecation warning。這是證據信心，不是進度百分比。

必要驗收項已完成，第一階段可宣告完成。進入第二階段前仍須由本人決定 auth 身分來源／session／角色規則，以及商品、採購、匯率、成本與庫存等業務規則；第一階段沒有替這些決策建立資料表或假實作。
