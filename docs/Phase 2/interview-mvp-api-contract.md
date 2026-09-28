# 三天面試 MVP API 合約

Base prefix：`/api/v1`。所有金額都是十進位字串；timestamps 是 UTC RFC 3339。成功 response 不包含推薦成本法。

正式驗證與授權尚未實作，以下端點只允許本機與受控 CI 展示，不可直接公開部署。

## 商品

### `POST /api/v1/products`

Request：

```json
{"name":"商品 A"}
```

成功 `201`：

```json
{"product_id":1,"name":"商品 A","created_at":"2026-09-28T04:00:00Z","updated_at":"2026-09-28T04:00:00Z"}
```

名稱會 trim；空白回 `422 validation_error`；不分大小寫重複回 `409 product_name_conflict`。

### `GET /api/v1/products`

成功 `200`，回傳按 ID 穩定排序的商品陣列。MVP 不提供 update/delete。

## 進貨批次

### `POST /api/v1/purchase-batches`

Request：

```json
{
  "product_id": 1,
  "quantity": 20,
  "unit_cost": "80.000000",
  "currency": "CAD",
  "purchased_at": "2026-09-27T01:00:00Z"
}
```

成功 `201` 回 batch ID、原始／剩餘數量、單位成本字串、CAD 與 UTC timestamps。商品不存在回 `404 product_not_found`。quantity 非正整數、cost 不大於零、非 CAD 或無效時間回 `422 validation_error`。

## 庫存

### `GET /api/v1/inventory`

成功 `200`，回全部商品的總剩餘量與批次摘要。

### `GET /api/v1/inventory/{product_id}`

成功 `200`：

```json
{
  "product_id": 1,
  "product_name": "商品 A",
  "total_remaining_quantity": 30,
  "batches": [
    {
      "batch_id": 1,
      "original_quantity": 20,
      "remaining_quantity": 20,
      "unit_cost": "80.00",
      "currency": "CAD",
      "purchased_at": "2026-09-27T01:00:00Z"
    }
  ]
}
```

批次依 `purchased_at ASC, batch_id ASC`。商品不存在回 `404 product_not_found`。

## 成本試算

### `POST /api/v1/simulations/cost`

Request：

```json
{
  "product_id": 1,
  "quantity": 25,
  "selling_unit_price": "120.00",
  "currency": "CAD"
}
```

成功 `200` 概念：

```json
{
  "product_id": 1,
  "quantity": 25,
  "currency": "CAD",
  "selling_unit_price": "120.00",
  "revenue": "3000.00",
  "fifo": {
    "method": "fifo",
    "unit_cost": "84.00",
    "total_cost": "2100.00",
    "gross_profit": "900.00",
    "gross_margin_percent": "30.00"
  },
  "weighted_average": {
    "method": "weighted_average",
    "unit_cost": "86.67",
    "total_cost": "2166.67",
    "gross_profit": "833.33",
    "gross_margin_percent": "27.78"
  },
  "difference": {
    "total_cost": {"amount":"66.67","higher_method":"weighted_average"},
    "gross_profit": {"amount":"66.67","higher_method":"fifo"}
  },
  "inventory_changed": false,
  "disclaimer": "此結果僅供成本比較，不是正式會計淨利。"
}
```

`difference` 使用絕對差額並明列較高的一方，避免正負號歧義；兩者相同時為 `equal`。它不是推薦欄位。

商品不存在回 `404 product_not_found`。總可用量不足回 `409 insufficient_inventory`，錯誤 details 只可包含安全的 requested/available 整數，不回 SQL 或內部例外。任何失敗都不得修改資料。

## 錯誤 envelope

沿用既有 request ID：

```json
{
  "error": {
    "code": "insufficient_inventory",
    "message": "Insufficient inventory",
    "request_id": "safe-request-id",
    "details": {"requested":31,"available":30}
  }
}
```

`details` 為可選安全欄位。驗證錯誤維持既有泛化訊息；response 與結構化 log 都不得包含 request body、stack trace、SQL、DB URL 或秘密值。

## 非合約端點

MVP 不提供 auth、order、stock deduction、simulation history、exchange rate、customer、warehouse、import 或 delete/update API。
