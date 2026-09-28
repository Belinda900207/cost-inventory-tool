# 成本與庫存工具

第一階段工程骨架：React + TypeScript + Vite 狀態頁、FastAPI 健康檢查、MySQL 8.4、SQLAlchemy 2、Alembic、隔離整合測試與 GitHub Actions。第二階段正在加入供受控面試展示使用的成本與庫存試算 MVP。

> **安全邊界：**正式驗證與授權尚未實作，本版本只能用於本機及受控展示，不可直接公開部署。

目前第二階段正在加入商品、CAD 進貨批次、庫存查詢與成本比較。正式訂單、扣庫存、匯率及登入尚未上線；Auth 仍只保留介面，`login`／`me` 不存在。

## 需求

- Git
- Python 3.14.4
- Node.js 24.21.0 與 npm
- Docker Desktop／Docker Engine，且可執行 `docker compose`

WSL 若 `docker` 顯示 Desktop integration 未啟用，但 `docker.exe version` 能取得 server 版本，可在本頁命令中暫以 `docker.exe` 取代 `docker`；仍建議在 Docker Desktop 設定中啟用該 WSL distribution 的 integration。

## 從 clone 啟動

```bash
git clone https://github.com/Belinda900207/cost-inventory-tool.git
cd cost-inventory-tool

python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
npm --prefix frontend ci

python3 scripts/init_dev_env.py
docker compose up -d --wait
(cd backend && .venv/bin/python -m alembic upgrade head)
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

## 面試 MVP API

以下端點目前沒有正式驗證或授權，只能用於本機及受控 CI：

| 方法／路徑 | 用途 |
| --- | --- |
| `POST /api/v1/products` | 建立不分大小寫防重的商品 |
| `GET /api/v1/products` | 查詢商品 |
| `POST /api/v1/purchase-batches` | 新增正整數數量、`DECIMAL(19,6)` CAD 成本的進貨批次 |
| `GET /api/v1/inventory` | 查詢全部商品總庫存與批次 |
| `GET /api/v1/inventory/{product_id}` | 查詢單一商品庫存與批次 |
| `POST /api/v1/simulations/cost` | 同時試算 FIFO 與數量加權平均；不保存、不扣庫存 |

目前沒有商品改名、刪除、正式訂單或扣庫存；試算只回傳客觀比較，不推薦成本法，且不會改變批次剩餘數量。

## 三至五分鐘展示流程

啟動服務並打開網頁後，全程可由畫面完成：

1. 建立「商品 A」。
2. 建立較早的 `20 × CAD 80` 與較晚的 `10 × CAD 100` 兩批進貨。
3. 確認總庫存 30、批次剩餘量 20 與 10。
4. 試算 1 個、成交單價 CAD 120：FIFO 單位成本 80.00，加權平均 86.67。
5. 試算 25 個：FIFO 總成本 2100.00，加權平均總成本 2166.67。
6. 試算 31 個：畫面顯示庫存不足，不回傳部分結果。
7. 再確認總庫存仍為 30；試算沒有建立訂單或扣除庫存。

畫面中的毛利是成本比較用試算，不是正式會計淨利；兩種成本法並列且沒有系統推薦。

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

### 第一階段

- [架構](docs/Phase%201/architecture.md)
- [決策紀錄](docs/Phase%201/decisions.md)
- [開發與 PR 流程](docs/Phase%201/development-workflow.md)
- [Human-in-the-loop AI 流程](docs/Phase%201/ai-workflow.md)
- [第一階段驗收](docs/Phase%201/stage-1-verification.md)
- [逐步實作紀錄](docs/Phase%201/stage-1-implementation-log.md)
- [Auth 待決策邊界](docs/Phase%201/auth-contract.md)

### 第二階段：三天面試 MVP

- [MVP 需求與追溯](docs/Phase%202/interview-mvp-requirements.md)
- [領域模型](docs/Phase%202/interview-mvp-domain-model.md)
- [API 合約](docs/Phase%202/interview-mvp-api-contract.md)
- [MVP-only 決策](docs/Phase%202/interview-mvp-decisions.md)
- [施工紀錄](docs/Phase%202/interview-mvp-implementation-log.md)
- [最終驗證](docs/Phase%202/interview-mvp-verification.md)
- [面試展示腳本](docs/Phase%202/interview-demo-script.md)
