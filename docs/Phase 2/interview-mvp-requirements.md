# 三天面試 MVP 需求與追溯

狀態：PR-MVP-0 合約基線。施工日期為 2026-09-28～2026-09-30。

本文件描述本機與 CI 受控展示用的垂直切片，不代表 Production 完整版本。正式驗證與授權尚未實作，本版本不可直接公開部署。

## 目標流程

```text
建立商品 → 輸入兩批進貨 → 保存至 MySQL → 查看庫存與批次
→ 輸入數量與 CAD 成交單價 → 並排比較 FIFO 與數量加權平均
→ 查看成本、營收、試算毛利及毛利率 → 證明試算不改庫存
```

## 功能需求

| ID | 需求 | 驗收證據 |
| --- | --- | --- |
| MVP-SCOPE-001 | 系統只客觀並列 FIFO 與數量加權平均，不推薦、不預選成本法 | UI 文案、component、browser test |
| MVP-SCOPE-002 | 試算毛利不得描述為正式會計淨利 | API disclaimer、UI test |
| MVP-PROD-001 | 商品具有內部 ID、名稱及 UTC 建立／更新時間 | migration、API/MySQL test |
| MVP-PROD-002 | 名稱 trim 後不可空白；大小寫不同視為重複 | service/API/MySQL unique test |
| MVP-PROD-003 | MVP 只提供商品建立與查詢 | route inventory、API contract |
| MVP-BATCH-001 | 批次保存商品、原始／剩餘正整數數量、單位成本、CAD、進貨時間及 timestamps | migration、API/MySQL test |
| MVP-BATCH-002 | 新批次剩餘數量等於原始數量；單位成本大於零 | constraints、service tests |
| MVP-BATCH-003 | 單位成本使用 `DECIMAL(19, 6)`；Python 使用 `Decimal`，不得以 float 計算 | schema inspection、unit tests |
| MVP-INV-001 | 庫存查詢顯示商品總剩餘量與每一批次完整資料 | API、component、browser test |
| MVP-INV-002 | 建立批次增加可試算庫存；試算不改總量或批次剩餘量 | MySQL before/after tests |
| MVP-FIFO-001 | FIFO 依 `purchased_at`、再依 batch ID 由小到大取用仍有庫存的批次 | pure unit tests |
| MVP-FIFO-002 | FIFO 支援單批、跨批、剛好用完及不足錯誤 | golden cases |
| MVP-WAC-001 | 加權平均為 `Σ(剩餘量 × 單位成本) ÷ Σ剩餘量`，不得使用單價簡單平均 | pure unit tests |
| MVP-SIM-001 | 輸入商品、正整數數量及大於零的 CAD 成交單價 | API validation tests |
| MVP-SIM-002 | 同一 response 同時回傳兩種方法的單位成本、總成本、營收、毛利與毛利率 | contract/API/UI tests |
| MVP-SIM-003 | 顯示成本差額與毛利差額及其方向，不替使用者決策 | contract/component tests |
| MVP-SIM-004 | 不建立訂單或試算歷史；重複試算 deterministic 且無資料副作用 | metadata、10-run MySQL test |
| MVP-SIM-005 | 庫存不足回安全且明確的錯誤，不回部分成功 | API/MySQL test |
| MVP-MONEY-001 | API 金額以字串傳輸；內部保留 6 位或足夠精度，顯示邊界 `ROUND_HALF_UP` 至 2 位 | serialization/rounding tests |
| MVP-TIME-001 | 所有資料庫時間保存 UTC，API 使用帶時區 RFC 3339 | model/API tests |
| MVP-CUR-001 | MVP 只接受 CAD，固定匯率 1，不呼叫外部匯率服務 | validation/dependency inventory |
| MVP-SEC-001 | 業務 API 無正式 auth，只限本機／受控 CI；README 必須醒目警告 | README review |
| MVP-ERR-001 | API 沿用安全 error envelope，不回 stack trace、SQL 或秘密 | error tests |

## 固定 golden data

- 商品：商品 A。
- 較早批次：20 個，CAD 80。
- 較晚批次：10 個，CAD 100。
- 總庫存：30。
- 加權平均原始單位成本：`(20×80 + 10×100) ÷ 30 = 86.666666…`。

| 案例 | 預期 |
| --- | --- |
| 數量 1、售價 120 | FIFO 成本 80.00、毛利 40.00、毛利率 33.33%；WAC 成本 86.67、毛利 33.33、毛利率 27.78% |
| 數量 25、售價 120 | FIFO 總成本 2100.00；WAC 總成本 2166.67；庫存仍為 30 |
| 數量 30 | 成功計算，實際庫存仍為 30 |
| 數量 31 | `insufficient_inventory`，無部分成功或資料修改 |
| 同一試算 10 次 | 每次結果相同，兩批剩餘量仍為 20 與 10 |

## PR 追溯

| PR | 需求 | 主要證據 |
| --- | --- | --- |
| PR-MVP-0 | 全部需求合約與邊界 | 文件、有效連結、CI 無退步 |
| PR-MVP-1 | PROD、BATCH、INV、TIME、CUR、SEC、ERR | migration、API/MySQL、component tests |
| PR-MVP-2 | FIFO、WAC、SIM、MONEY、ERR | pure unit、API、MySQL 無副作用 tests |
| PR-MVP-3 | SCOPE、INV、SIM、SEC 端到端 | component、Playwright、clean clone、CI artifact |

## 明確延後

正式登入／Session／Cookie／CSRF／帳號與角色、正式訂單與扣庫存、取消／更正／回復、idempotency、row locking、超賣控制、即時匯率、非 CAD、多倉庫、多租戶、客戶入口、運費、關稅、折扣、手續費、稅務、退貨、匯入、雲端、正式網域、備份及大型 UI 美化全部不在本 MVP。
