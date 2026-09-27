# 第一階段架構

```mermaid
flowchart LR
  Browser[React 狀態頁] -->|/api/health/*| Vite[Vite 開發 proxy]
  Vite -->|/health/*| API[FastAPI]
  API --> Live[/health/live]
  API --> Ready[/health/ready]
  Live --> Process[Process 狀態]
  Ready -->|SQLAlchemy SELECT 1| DB[(MySQL 8.4)]
  API --> Obs[Request ID / JSON log / error envelope]
  Alembic[Alembic] -->|共用 Settings 與 Base.metadata| DB
```

React 只呼叫同源相對路徑；元件不含完整 backend URL。Vite 開發環境把 `/api/health/...` 轉成 backend `/health/...`，並保留未來業務 API 的 `/api/v1/...`。正式部署需要同源反向代理，部署與 CD 不在第一階段。

FastAPI 由 `create_app()` 組裝 router 與 middleware。`/health/live` 不讀設定、不建立 engine、不連 DB；`/health/ready` 從可替換 dependency 取得 DB probe。DB engine 延後建立，使用 `pool_pre_ping` 與 1–10 秒設定逾時。

可觀測性 middleware 驗證或產生 request ID，放入 response header；安全 error envelope 也包含 ID。結構化 log 只記時間、level、service、environment、request ID、method、路由模板、status、duration 與固定 message。

Alembic 與 API 共用 `Settings.database_url` 及 `Base.metadata`。第一階段 metadata 與 migration history 都是空的；schema 後續只能用經審查的 migration 管理，不用 `create_all()`。

Auth 只有 schema、Protocol、dependency 與空 router。未配置 service 時拒絕請求；目前無 endpoints、帳號、table 或 session 儲存。

測試資料庫是 Compose project `cost-inventory-test`：port 3307、`test_app`、`cost_inventory_test`、獨立 volume。Integration 與 browser tests 在操作前 assert 這些值，只 stop/restart 該 project，且不刪 volume。
