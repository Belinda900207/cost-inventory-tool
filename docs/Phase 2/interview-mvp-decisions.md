# 三天面試 MVP 決策

本文件決策只對 2026-09-28～2026-09-30 的受控展示 MVP 有效，不是 Production 永久架構。

| ID | MVP-only 決策 | 原因 | 替代方案／限制 |
| --- | --- | --- | --- |
| MVP-D001 | 四支小 PR：合約、庫存基礎、成本 API、比較 UI | 每支單一目的且能個別驗證 | 不合成大型 PR；功能 PR 必須等前置 PR 合併 |
| MVP-D002 | 正式 auth 全部延後，API 只能本機／受控 CI | 三天內優先完成可證明的成本垂直切片 | 不建立假登入、假帳號或 JWT/localStorage |
| MVP-D003 | DB 金額 `DECIMAL(19, 6)`、Python `Decimal`、API 字串 | 保留精確值並避免 JSON binary float 問題 | Production precision 仍需重新評估 |
| MVP-D004 | 顯示使用 `ROUND_HALF_UP` 兩位；中間值不可先 round | 固定案例可重現且符合商務顯示 | Production 結帳捨入政策未決 |
| MVP-D005 | 只接受 CAD，匯率固定 1，不呼叫外部 API | 聚焦成本算法，避免把未批准 provider 當正式方案 | 非 CAD 與歷史匯率鎖定延後 |
| MVP-D006 | 試算完全不持久化 | 最直接證明試算無副作用 | 無 simulation table、history 或 order |
| MVP-D007 | FIFO 次序為 `purchased_at ASC, batch_id ASC` | 同時刻仍 deterministic | 正式扣庫存及 row locking 延後 |
| MVP-D008 | 商品保存 display name 與唯一 normalized name | 同時支援原顯示及不分大小寫防重 | Unicode normalization 細節由 PR-MVP-1 測試固定 |
| MVP-D009 | 差額以絕對值＋`higher_method` 表達 | 避免 signed difference 被誤讀為推薦 | 不顯示「較佳」「推薦」或預設選取 |
| MVP-D010 | PurchaseBatch 是庫存事實來源，MVP 無 aggregate stock 欄位 | 避免兩份庫存資料失同步 | 查詢成本可在正式規模後再評估 read model |
| MVP-D011 | 所有 schema 只由 Alembic 管理 | 可重建、可審查、可在真實 MySQL 驗證 | 禁止 `create_all()` 代替 migration |
| MVP-D012 | 真實 MySQL 與 Playwright 沿用既有隔離 CI | 不接觸開發資料或刪 volume | skipped integration 不算通過 |

## 延後的正式決策

身分來源、Session/Cookie/CSRF、角色、密碼演算法、訂單、扣庫存、idempotency、row locking、即時匯率、Production 金額精度、雲端、網域及備份都沒有被本 MVP 決定。
