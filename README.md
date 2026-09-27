# 成本與庫存工具

第一階段工程骨架：React + TypeScript + Vite 狀態頁、FastAPI 健康檢查、MySQL 8.4、SQLAlchemy 2、Alembic、隔離整合測試與 GitHub Actions。

目前沒有商品、進貨、匯率、庫存、成本、訂單或正式登入功能，也沒有業務資料表。Auth 只保留介面；`login`／`me` 尚未上線。

## 需求

- Git
- Python 3.14.4
- Node.js 24.21.0 與 npm
- Docker Desktop／Docker Engine，且可執行 `docker compose`

## 從 clone 啟動

```bash
git clone https://github.com/Belinda900207/cost-inventory-tool.git
cd cost-inventory-tool

python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
npm --prefix frontend ci

python3 scripts/init_dev_env.py
docker compose up -d --wait
```

`init_dev_env.py` 只在 `.env` 不存在時建立隨機本機密碼，權限為 `0600`；已存在時不讀取、不覆寫。不要提交 `.env`，也不要把值貼到 issue、PR 或 log。

開兩個終端：

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

開啟 <http://127.0.0.1:5173>。畫面會經 Vite `/api` proxy 顯示 FastAPI 與 MySQL 狀態。

停止開發資料庫但保留 volume：

```bash
docker compose stop
```

## 環境變數

| 名稱 | 用途 | 範例／預設 |
| --- | --- | --- |
| `MYSQL_ROOT_PASSWORD` | MySQL container 初始化 root 密碼 | 必填、隨機產生 |
| `MYSQL_DATABASE` | 應用資料庫 | `cost_inventory` |
| `MYSQL_USER` | 最小權限應用帳號 | `app_user` |
| `MYSQL_PASSWORD` | 應用帳號密碼 | 必填、隨機產生 |
| `MYSQL_HOST` | API 連線主機 | `127.0.0.1` |
| `MYSQL_PORT` | API 連線 port | `3306` |
| `DATABASE_TIMEOUT` | DB 連線／讀寫逾時秒數 | `3`，允許 1–10 |
| `ENVIRONMENT` | 程序環境變數；結構化 request log 的環境名稱 | 未設定時 `development` |

`.env.example` 只提供資料庫欄位說明；建議用初始化 script 產生本機值。`ENVIRONMENT` 是啟動 API 時可另外設定的程序環境變數。

## 健康 API

| 路徑 | 意義 | DB 失敗時 |
| --- | --- | --- |
| `GET /health/live` | Python process 可回應，不連 DB | 仍為 `200` |
| `GET /health/ready` | 真實執行 `SELECT 1` | `503` 安全 error envelope |
| `GET /health` | 第一版相容合約 | `503 {"status":"unhealthy","database":"unavailable"}` |

每個 response 都有 `X-Request-ID`。一般錯誤 body 也帶同一 ID。自訂 ID 只接受單一、1–64 字元的英數、底線或連字號；log 不記 query、request body、例外文字或完整 DB URL。

## 驗證

後端單元/API 與品質檢查：

```bash
cd backend
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check . ../scripts
.venv/bin/python -m ruff format --check . ../scripts
.venv/bin/python -m alembic heads
```

前端：

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
cd ..
python3 scripts/check_repository.py
```

隔離 MySQL integration 使用不同 project、port `3307`、帳號、database 與 named volume，不操作開發 DB：

```bash
python3 scripts/init_test_env.py
docker compose --env-file .env.test -p cost-inventory-test -f compose.test.yaml up -d --wait --wait-timeout 150
cd backend
RUN_MYSQL_INTEGRATION=1 .venv/bin/python -m pytest -q -s tests/integration
```

真實瀏覽器流程：

```bash
cd frontend
npx playwright install --with-deps chromium
RUN_MYSQL_E2E=1 npm run test:e2e
```

測試完成後可用以下命令停止測試 DB；不會刪除 volume：

```bash
docker compose --env-file .env.test -p cost-inventory-test -f compose.test.yaml stop
```

GitHub Actions 對 PR 與 `main` 執行 backend、frontend、mysql-integration、browser-integration。瀏覽器工作保存健康、載入、DB 失敗與後端斷線截圖 14 天。

## 文件

- [架構](docs/architecture.md)
- [決策紀錄](docs/decisions.md)
- [開發與 PR 流程](docs/development-workflow.md)
- [Human-in-the-loop AI 流程](docs/ai-workflow.md)
- [第一階段驗收](docs/stage-1-verification.md)
- [逐步實作紀錄](docs/stage-1-implementation-log.md)
- [Auth 待決策邊界](docs/auth-contract.md)
