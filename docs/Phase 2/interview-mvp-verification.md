# 三天面試 MVP 最終驗證

狀態：PR-MVP-3 施工中；所有「待 PR CI」項目必須取得實際證據後才會改為通過。

## 可驗證範圍

本 MVP 是本機與受控 CI 用的成本比較垂直切片。它能建立商品與 CAD 進貨批次、保存至 MySQL、查詢庫存，並同時試算 FIFO 與數量加權平均。試算不保存、不扣庫存、不推薦成本法。

它不是可公開部署的 Production 系統；正式 auth、訂單、併發扣庫存、匯率、稽核與雲端均未實作。

## Repository 與 PR 證據

| PR | 分支 | 主要 commit | 狀態／證據 |
| --- | --- | --- | --- |
| [#14](https://github.com/Belinda900207/cost-inventory-tool/pull/14) | `docs/interview-mvp-contract` | `a3ef213`、`d4a7eab` | 已合併；main run `36381274891` 全綠 |
| [#15](https://github.com/Belinda900207/cost-inventory-tool/pull/15) | `feat/interview-inventory-foundation` | `2bc3da9`、`0978861`、`3738ba8` | 已合併；main run `36387141160` 全綠 |
| [#16](https://github.com/Belinda900207/cost-inventory-tool/pull/16) | `feat/interview-cost-simulation` | `b95e916`、`c86f7ae` | 已合併；main run `36425691886` 全綠 |
| PR-MVP-3 | `feat/interview-cost-comparison-ui` | 待填 | 比較 UI、完整 browser flow、clean clone 與本文件 |

## 資料庫與 migration

- Alembic head：`20260928_01_inventory`。
- 業務資料表只有 `products` 與 `purchase_batches`；另有 `alembic_version`。
- `products.normalized_name` 唯一；批次有商品 FK、正數成本、原始／剩餘量範圍與 CAD constraints。
- 金額保存為 `DECIMAL(19,6)`；時間以 UTC connection convention 保存。
- 沒有 `orders`、`simulation_history`、users、customers、warehouses 或 exchange rates 表。

## API 摘要

| 方法／路徑 | 用途 |
| --- | --- |
| `POST /api/v1/products` | 建立正規化、防重商品 |
| `GET /api/v1/products` | 查詢商品 |
| `POST /api/v1/purchase-batches` | 建立 CAD 進貨批次 |
| `GET /api/v1/inventory` | 查詢所有庫存與批次 |
| `GET /api/v1/inventory/{product_id}` | 查詢單一商品庫存 |
| `POST /api/v1/simulations/cost` | 同時回 FIFO／加權平均；純試算 |

所有金額以字串傳輸；錯誤使用含 request ID 的安全 envelope。庫存不足為 `409 insufficient_inventory`，只回 requested/available 安全整數。

## 固定案例實際輸出

庫存固定為較早 `20 × CAD 80`、較晚 `10 × CAD 100`，共 30。

| 數量／售價 | FIFO | 數量加權平均 | 結果 |
| --- | --- | --- | --- |
| 1／CAD 120 | 單位與總成本 80.00；毛利 40.00；毛利率 33.33% | 單位與總成本 86.67；毛利 33.33；毛利率 27.78% | 成功，庫存仍 30 |
| 25／CAD 120 | 單位 84.00；總成本 2100.00；毛利 900.00；毛利率 30.00% | 單位 86.67；總成本 2166.67；毛利 833.33；毛利率 27.78% | 成本／毛利差額皆 66.67 |
| 30 | 總成本 2600.00 | 總成本 2600.00 | 剛好使用全部可用量的試算成功；實際庫存仍 30 |
| 31 | 無部分成功 | 無部分成功 | `409 insufficient_inventory`，requested 31／available 30 |

## 無副作用證據

PR #16 的 MySQL integration 在真實 MySQL 8.4 中：

1. 建立商品與兩批資料。
2. 對相同 payload 連續呼叫試算 API 十次並逐一比較 response。
3. 再執行剛好 30 與不足 31 的案例。
4. 試算前後比較每個 batch 的 ID、商品、原始量、剩餘量、成本、幣別與三個 timestamps。
5. 確認資料表集合仍只有 `alembic_version`、`products`、`purchase_batches`。

結果：run `36425383383` 與合併後 main run `36425691886` 的 mysql-integration 均通過，沒有 skip；兩批剩餘量保持 20／10。

## 測試矩陣

| 層級 | 本機結果 | CI／限制 |
| --- | --- | --- |
| Backend pytest | 39 passed、3 skipped、1 warning | skip 是三支 opt-in MySQL tests；既有 Starlette/httpx deprecation warning |
| Ruff | 45 files lint／format passed | 待 PR-MVP-3 CI |
| Frontend Vitest | 14 passed | 待 PR-MVP-3 CI |
| Oxlint／TypeScript／build | passed；22 modules | 待 PR-MVP-3 CI |
| MySQL integration | 本機 Docker Desktop daemon 未啟動，未通過 | PR #16 已真實通過；PR-MVP-3 CI 待跑 |
| Playwright | 本機缺 `libnspr4.so`；real-stack 明確 skip，另一案例 failed，未稱為通過 | PR-MVP-3 CI 會安裝 Chromium dependencies 並執行 real stack |
| Repository scan | tracked artifact 與 bundle heuristic secret scan passed | 待 PR-MVP-3 CI |

## Browser 與截圖證據

PR-MVP-3 Playwright 會保存：健康狀態、1 個商品成本比較、25 個跨批比較、十次試算後庫存不變、資料庫故障及後端斷線等截圖。CI artifact 名稱為 `browser-evidence`，保留 14 天。最終 run URL 與實際檔名待 CI 後填入。

## Clean-clone 驗收

待功能 commit push 後，從 remote branch clone 至新的 `/tmp` 目錄，依 README 執行 Python/Node 安裝、Ruff、pytest、Oxlint、typecheck、Vitest、build、Alembic head 與 application import/start smoke。Docker daemon 未啟動時，不把本機 migration upgrade 或 MySQL 啟動稱為通過；由隔離 CI 補足真實 MySQL 證據。

## 已完成與未完成

已完成：商品、進貨批次、MySQL migration/persistence、庫存查詢、pure FIFO、pure weighted average、Decimal response、無副作用試算 API、安全錯誤、比較 UI 與自動測試。

未完成：正式身分驗證與權限、正式訂單與扣庫存、idempotency／row locking／超賣防護、取消更正與 audit、即時匯率、非 CAD、多倉庫、多租戶、客戶功能、雲端部署、網域與備份。這些不得由 MVP 推定為已完成。

## 完成度與信心

PR-MVP-3 CI 與 clean-clone 證據完成前：三天面試 MVP 94%；證據信心 92/100。扣分是完整 real-stack browser、artifact 與 clean-clone 尚待實跑，不是已知成本公式缺陷。
