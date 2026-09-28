# 三至五分鐘面試展示腳本

## 展示前準備

- 依 README 啟動 MySQL、執行 `alembic upgrade head`，再啟動 FastAPI 與 Vite。
- 使用空白或專用展示資料庫；不要清除或覆蓋真實資料。
- 確認畫面顯示 FastAPI「運作中」、MySQL「連線正常」。
- 若「商品 A」已存在，使用帶時間或面試代號的唯一名稱，不要刪既有資料。

## 0:00–0:30｜問題與邊界

說法：

> 同一商品可能分批進貨且成本不同。這個 MVP 同時提供 FIFO 與數量加權平均的客觀試算，讓內部使用者比較；系統不替使用者指定正式成本法。它不是會計系統，畫面毛利也不是正式會計淨利。

指出頁首 health 狀態，說明瀏覽器、API 與 MySQL 都在線。

## 0:30–1:30｜建立真實庫存

1. 建立「商品 A」。
2. 建立較早批次：20 個、CAD 80。
3. 建立較晚批次：10 個、CAD 100。
4. 指出畫面總庫存 30、兩批原始／剩餘量 20 與 10。

說法：

> 商品與每批進貨實際保存於 MySQL，schema 只由 Alembic 管理。批次分開保存，是因為 FIFO 需要時間順序，加權平均需要數量權重。

## 1:30–2:30｜比較兩種成本

先輸入數量 1、CAD 120：

- FIFO 單位成本 CAD 80.00。
- 數量加權平均單位成本 CAD 86.67。
- FIFO 試算毛利 40.00／33.33%；加權平均 33.33／27.78%。

接著輸入數量 25、CAD 120：

- FIFO 跨批總成本：`20×80 + 5×100 = 2100.00`。
- 加權平均總成本 2166.67。
- 指出兩欄尺寸與地位相同，差額只描述哪一方較高，不使用推薦標籤。

說法：

> 後端全程用 Decimal；86.67 只在 response 邊界 ROUND_HALF_UP 顯示，中間計算沒有先把加權成本截成兩位。

## 2:30–3:15｜錯誤與無副作用

輸入數量 31，展示「需要 31，目前可用 30」的庫存不足訊息。再回看庫存仍為 30、兩批仍為 20／10。

說法：

> 試算 service 只有唯讀查詢，不建立訂單或試算紀錄。MySQL integration 會連續試算十次，逐欄比較前後 batch rows，並確認沒有新增資料表。

## 3:15–4:15｜工程證據

展示：

- pure cost engine 的 golden tests。
- Alembic revision 與 MySQL integration。
- PR #14～#17 的小步拆分與全綠 CI。
- Playwright `browser-evidence` artifact 的比較與庫存不變截圖。

說法：

> 我把純算法、HTTP 合約、真實資料庫與瀏覽器流程分層驗證。Mock 測試不冒充 integration；本機不能跑 Docker 或 Chromium dependencies 時，我保留失敗紀錄，最後以 CI 的隔離環境補足證據。

## 4:15–5:00｜誠實收尾

> 這是三天內完成的面試 MVP，不可直接公開部署。正式 auth、訂單、併發扣庫存、取消更正與 audit、即時匯率、雲端和備份都刻意留在下一階段；我沒有用假登入或硬編碼結果冒充完成。

## 常見追問與誠實回答

### 為什麼不用 float？

二進位浮點無法精確表示許多十進位金額。資料庫用 `DECIMAL(19,6)`、Python 用 `Decimal`、API 用字串，最後顯示才 round。

### 怎麼證明試算不扣庫存？

service 沒有 write method；更重要的是 MySQL integration 在十次 API 呼叫前後逐欄比較批次 rows，並驗證資料表沒有 order/history。

### 多人同時買最後一件會怎樣？

本 MVP 沒有正式訂單或扣庫存，所以沒有宣稱解決。Production 需要 transaction、row locking、idempotency 與真實 MySQL 競爭測試。

### 為什麼沒有登入？

三天範圍優先證明成本核心。正式 Session/Cookie/CSRF、密碼與角色尚未核定；加入假 auth 會製造錯誤安全感，因此只允許本機／受控 CI。

### 哪個成本法比較好？

系統不做會計政策決策，只客觀並列結果。正式成本法需要公司的會計政策與專業判斷。

### 加權平均為何不是 90？

因為批次數量不同：`(20×80 + 10×100) ÷ 30 = 86.666…`，不是 `(80+100)÷2`。

## 最應理解的十個工程概念

1. 垂直切片：從 UI、API 到 MySQL 完成一條可展示流程。
2. Migration：schema 是可版本化、可重建的程式碼，不靠 `create_all()`。
3. Domain invariant：正數、CAD、剩餘量範圍同時由應用與資料庫保護。
4. Pure function：成本引擎與框架、資料庫解耦，固定輸入即可重現。
5. Decimal precision：中間值與顯示 rounding 是不同責任。
6. Determinism：FIFO 以時間及 ID 破同分；相同輸入十次得到相同結果。
7. Side effect：試算只讀，正式命令與查詢必須有清楚邊界。
8. Test pyramid：pure、service、API、MySQL、browser 各自捕捉不同錯誤。
9. Safe error envelope：使用者得到穩定 code/request ID，不洩露 SQL 或內部例外。
10. Honest scope：未做的 auth、訂單與併發明列，測試 skip 也不冒稱通過。
