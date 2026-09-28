# 三天面試 MVP 施工紀錄

## Step MVP-00：接手與安全基線

### 這一步在做什麼

像開工前先確認地址、鑰匙和現場物品，避免把前一位留下的材料誤當垃圾清掉。

### 專業意義

確認 Git、遠端、工作樹、秘密檔案邊界及既有品質基線，將既有問題與本次變更分開。

### 為什麼現在做

後續會建立分支、migration 與四支 PR；若起點不正確，所有證據都會失去可追溯性。

### 執行前狀態

- 路徑：`/home/gunter/projects/cost-inventory-tool`。
- `main`／遠端 `origin/main`／HEAD 均為 `2bb0d5dc7c4164ab7dc60eae4103dd1357af9b13`。
- staged files 為空。
- 唯一 working tree 變更是七份 `docs/*.md` 搬至 `docs/Phase 1/`。
- 七份搬移檔案逐一以 `git show HEAD:<old-path> | cmp <new-path>` 證明 byte-identical。
- `.env` 與 `.env.test` 只檢查存在、ignore、未追蹤；未讀取或輸出值。

### 計畫

沿用現有 FastAPI／SQLAlchemy／Alembic／MySQL 與 React／Vite 結構，不重建專案。先完成文件合約 PR，再依序做庫存、成本試算及 UI。

### 實際修改

本步只稽核，沒有修改 source、schema、Git index 或 Git history。

### 執行指令

- `git status --short --branch`：區分 staged、tracked 與 untracked 修改。
- `git ls-remote --heads origin refs/heads/main`：唯讀核對遠端 main。
- `cmp`：逐位元核對搬移前後文件。
- backend Ruff／pytest／Alembic heads 與 frontend lint／typecheck／Vitest／build：建立功能施工前基線。

### 驗證結果

- Backend Ruff：22 files passed。
- Backend pytest：18 passed、0 failed、1 skipped、1 warning；skip 是 opt-in MySQL integration，沒有稱為通過。
- Warning：Starlette TestClient 使用 httpx 的既有 deprecation warning。
- Alembic heads：成功且無 revision。
- Frontend Oxlint、TypeScript、build：通過；Vitest 7 passed、0 failed。
- 遠端 main run `36324431010`：backend、frontend、mysql-integration、browser-integration 全綠。

### 失敗與修正

第一次在受限 sandbox 執行 pytest 卡在既有 TestClient 執行環境問題；停止該測試程序後，在核准的外部執行環境以相同測試重跑成功。這不是產品測試失敗。

### 我在面試時可以怎麼解釋

- 我先確認遠端與本機 commit 相同，沒有從錯誤基線開發。
- 我保留使用者已整理的文件，並以 byte comparison 證明內容沒被改寫。
- 我把 skipped integration 與真正通過的測試分開報告。
- 我沒有讀取或提交本機秘密設定。

### 風險與未完成

此時仍沒有商品、批次、成本引擎或試算 UI；Starlette/httpx warning 是既有技術債。

### 狀態與證據信心

完成，信心 98/100；扣分來自本機 sandbox TestClient 限制與既有 deprecation warning。

## Step MVP-01：PR-MVP-0 文件整理與合約

### 這一步在做什麼

像先畫好施工圖與驗收表，再開始砌牆，確保四支 PR 對「完成」有同一個定義。

### 專業意義

建立需求追溯、領域邊界、API contract 與 Architecture Decision Record，避免三天 MVP 偷渡正式系統功能或改變成本公式。

### 為什麼現在做

PR-MVP-1 的 schema 與 PR-MVP-2 的計算結果都依賴固定的欄位、精度、排序與錯誤語意。

### 執行前狀態

從 `main` commit `2bb0d5d` 建立 `docs/interview-mvp-contract`，保留預期的 Phase 1 文件搬移，index 原本為空。

### 計畫

- 納入七份 Phase 1 文件搬移。
- 修正 README 連結並加入未實作 auth 的醒目警告。
- 新增 requirements、domain model、API contract、MVP decisions 與本紀錄。
- 不修改 backend、frontend 或 migration。

### 實際修改

- `README.md`：修正 Phase 1 路徑，加入 Phase 2 文件索引與展示安全邊界。
- `docs/Phase 1/`：保留七份 byte-identical 第一階段文件。
- `interview-mvp-requirements.md`：需求 ID、固定案例、PR 與測試追溯。
- `interview-mvp-domain-model.md`：兩個持久化實體、純計算模型與無副作用 invariant。
- `interview-mvp-api-contract.md`：商品、批次、庫存與試算 API 及安全錯誤。
- `interview-mvp-decisions.md`：MVP-only 技術選擇與正式版本邊界。
- `interview-mvp-implementation-log.md`：保留實際施工、失敗與面試說法。

### 執行指令

本步使用 `git switch -c docs/interview-mvp-contract` 建立單一目的分支，並以 `apply_patch` 編輯文件。驗證使用：

- `git diff --check`：檢查工作樹 whitespace errors。
- `git show HEAD:<old-path> | cmp - <new-path>`：證明 Phase 1 搬移只改路徑。
- `test -f`：逐一確認 README 連結目的檔存在。
- backend `ruff check`、`ruff format --check`、`pytest -q`、`alembic heads`。
- frontend `npm run lint`、`npm run typecheck`、`npm test`、`npm run build`。
- `git add -- <逐一列出的 20 個舊／新路徑>`：以精確 pathspec stage，不使用 `git add .`。
- `git diff --cached --find-renames --name-status`：確認七份舊文件都被辨識為 R100 rename。
- `git diff --cached --check` 與完整 cached diff：檢查 whitespace 與即將提交的實際內容。
- staged path 與強秘密模式掃描：只輸出違規路徑或命中檔名，不讀 ignored `.env`。
- `git commit -m "docs: define interview MVP contract"`：建立首個文件 commit `a3ef213`。
- `git push -u origin docs/interview-mvp-contract`：推送單一目的分支。
- `gh pr create`：建立 PR #14，描述包含 Why、What、How to verify、Risks、Boundaries 與 Evidence。
- `gh pr checks 14 --watch`：監看四個遠端品質閘門。

### 驗證結果

- 12 個 README 文件連結目的檔全部存在。
- 七份 Phase 1 文件全部 byte-identical。
- `git diff --check` 通過；backend、frontend、migration 路徑沒有修改。
- Backend Ruff：22 files passed；Alembic heads 成功且仍無 revision。
- Backend pytest：18 passed、0 failed、1 skipped、1 warning；skip 是未啟用的隔離 MySQL integration，沒有冒稱通過。
- Frontend Oxlint、TypeScript 與 production build 通過；Vitest 7 passed、0 failed。
- 暫存區共 13 個結果路徑：README、七個 R100 rename、五份新文件；493 insertions、8 deletions。
- cached whitespace、禁止的 env／產物路徑及強秘密模式檢查全部無命中。
- PR：https://github.com/Belinda900207/cost-inventory-tool/pull/14 。
- CI：https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36380890716 。
- 首輪 CI 全綠：backend 25 秒、frontend 18 秒、mysql-integration 1 分 9 秒、browser-integration 1 分 36 秒。

### 失敗與修正

無本 PR 引入的失敗。pytest 保留既有 Starlette/httpx deprecation warning，沒有為文件 PR 升級相依套件或壓制警告。

### 我在面試時可以怎麼解釋

- 我先把 MVP-only 與正式版本邊界寫清楚，避免展示版被誤認為可公開部署。
- 每個需求都有後續 API、資料模型或測試證據。
- 計算精度與差額方向先寫成合約，前後端才不會各自解讀。

### 風險與未完成

PR-MVP-0 不含任何業務實作；功能仍須由後三支 PR 完成。

### 狀態與證據信心

PR-MVP-0 實作與首輪 CI 完成；待 evidence commit 的最終 CI 與合併後 main 驗證。現階段信心 99/100，扣分是尚未取得合併後 main 證據。

合併補充：PR #14 以 merge commit `9de3cb18004afb5132e94d2c8050ab515f33a98e` 進入 `main`；合併後 run `36381274891` 的 backend、frontend、mysql-integration、browser-integration 全綠。PR-MVP-0 完成，證據信心 100/100。

## Step MVP-02：商品、進貨批次與庫存基礎

### 這一步在做什麼

像先建立有編號的貨架與入庫單：商品是貨架標籤，每次進貨是獨立批次，庫存畫面把同一商品的批次加總但仍保留來源。

### 專業意義

以 Alembic 建立可重建 schema，並用 repository／service／router 分層隔離 SQL、業務規則與 HTTP。資料真的保存於 MySQL，不能以記憶體假資料代替。

### 為什麼現在做

FIFO 與加權平均都依賴批次時間、剩餘數量及精確成本；若資料模型未先固定，後續計算無法可靠驗證。

### 執行前狀態

- 分支：`feat/interview-inventory-foundation`。
- 起點：乾淨且已同步的 `main` commit `9de3cb1`。
- PR-MVP-0 與合併後 main 四項 CI 均全綠。
- schema 與 Alembic history 在本步開始前仍為空。

### 計畫

- 先加入 service、API、migration metadata、MySQL persistence 與 React component 驗收測試，確認預期紅燈。
- 建立 Product/PurchaseBatch models、migration、repository、service、router 與安全 domain errors。
- 建立最小商品／批次輸入及庫存檢視 UI。
- 本機完成不需秘密的 checks；真實 MySQL migration/persistence 由隔離 CI 驗證。

### 實際修改

- `app/inventory/models.py`：建立 Product 與 PurchaseBatch ORM；金額為 `DECIMAL(19,6)`，時間採 UTC convention，加入正數、剩餘量、CAD、FK、unique 與查詢 index。
- `migrations/versions/20260928_01_inventory.py`：第一個正式 revision，可由空資料庫建立及 downgrade 兩張表。
- `app/inventory/repository.py`：集中 SQLAlchemy add、transaction 與 deterministic inventory queries。
- `app/inventory/service.py`：商品名稱 trim＋Unicode NFKC＋`casefold()`，建立商品／批次並處理 unique conflict。
- `app/inventory/router.py`、`schemas.py`、`dependencies.py`：五個 API、Decimal 字串、UTC response 與 service dependency。
- `app/observability.py`：擴充既有安全 envelope，支援受控 domain error code 及安全整數 details；既有錯誤合約不變。
- `app/db.py`：每個 request 取得短生命週期 SQLAlchemy Session，DB connection session 固定 UTC。
- backend unit/API/migration tests：名稱正規化、unique rollback、缺少商品、validation、字串金額及 metadata/revision。
- MySQL integration：空 DB upgrade、兩批持久化、重連仍為 30、資料庫 constraints 直接拒絕壞資料、最後只清理自己建立的測試 rows。
- `run_browser_backend.py`：隔離 DB 身分檢查通過後先執行 `alembic upgrade head`，避免 health 正常但業務表不存在的假綠燈。
- `frontend/src/features/inventory/`：API client、商品與批次表單、總庫存／批次列表、錯誤狀態、3 個 component tests。
- `App.tsx` 與 CSS：保留 health 狀態並掛載最小 inventory UI；health tests mock 子元件以維持單元邊界。
- README：clone 流程加入 `alembic upgrade head`，列出 MVP API 與未實作 auth／扣庫存警告。

### 執行指令

- Targeted pytest 與 Vitest：先執行新測試，證明模組尚不存在的預期紅燈。
- `ruff check --fix`／`ruff format`：只整理 import 與機械格式，再以無 `--fix` 的指令重驗。
- backend `ruff check . ../scripts`、`ruff format --check . ../scripts`、`pytest -q`、`alembic heads`。
- frontend `npm run lint`、`npm run typecheck`、`npm test`、`npm run build`。
- 真實 migration／MySQL constraint／持久化測試已寫為 opt-in integration，將由 PR CI 的隔離 MySQL job 執行。

### 驗證結果

- 預期紅燈：backend 3 個 collection errors（`app.inventory` 尚不存在）；frontend 1 failed suite（`InventoryPanel` 尚不存在）。
- Targeted backend 完成後：7 passed、0 failed、1 warning。
- 完整 backend：24 passed、0 failed、2 skipped、1 warning；兩個 skip 是未在本機啟用的隔離 MySQL tests，沒有稱為通過。
- Ruff：34 files lint／format passed；Alembic head 為 `20260928_01_inventory`。
- Frontend：10 passed、0 failed；Oxlint、TypeScript 與 production build 通過，21 modules。
- PR CI run `36382803280`：backend 26 秒、frontend 12 秒、mysql-integration 1 分 11 秒、browser-integration 1 分 34 秒，四項全綠。MySQL integration 真實執行 migration、constraints、持久化與重連案例，並非 skip。

### 失敗與修正

- 第一輪 Ruff 發現 service 少匯入 `UTC`，以及 6 個機械格式差異；補正 UTC conversion 後用 Ruff 整理並重驗全綠。
- Oxlint 指出 effect 直接呼叫 state-updating helper 可能造成 cascading render；改為外部 API Promise 完成後才更新 state，warning 消失。
- Staged diff 審查發現 browser helper 原本只啟動 API、不套用 schema；加入受控 test DB migration，成功才啟動 Uvicorn。
- 沙箱內 targeted pytest 在 4 個 service tests 後卡於既有 TestClient 環境限制；停止該次後在核准環境重跑 7 passed。沒有把半截輸出算成功。
- PR #15 首輪 CI run `36382428980` 的 backend、frontend、browser-integration 通過，mysql-integration 有 1 項失敗。migration、商品與批次寫入、重連後總量 30 皆已成功；失敗發生於資料庫正確拒絕違反 constraint 的 row 時，PyMySQL 將 MySQL 3819 分類成 `OperationalError`，但測試只接受 `IntegrityError`。斷言改接 SQLAlchemy 共同基底 `DBAPIError`，仍只在資料庫確實拒絕壞資料時通過，並等待 CI 重驗。
- 修正後 targeted Ruff lint／format 通過；完整 backend 為 24 passed、2 個未啟用 MySQL 的明確 skip、1 個既有相依套件 deprecation warning。沙箱內同樣會卡於 TestClient，因此停止後在允許 loopback 的環境重跑，未將中止程序列為成功。

### 我在面試時可以怎麼解釋

- 我先寫會失敗的驗收測試，讓 schema、API 與 UI 的完成條件可以被執行。
- 商品與批次分開保存，才能重現 FIFO 次序與加權平均的數量權重。
- 庫存總量是批次剩餘量的查詢結果，不額外維護容易失同步的總數欄位。

### 風險與未完成

此 PR 不做成本試算、訂單、扣庫存、auth 或併發控制。

### 狀態與證據信心

本機 unit/API/component/品質檢查與 PR CI 全綠；乾淨 MySQL 8.4 已證明 migration、持久化、constraints 與重連，browser integration 也通過。現階段信心 98/100，保留 2 分是 MVP 尚未進入下一支成本計算 PR，這不屬於本 PR 邊界。

合併補充：PR #15 以一般 merge commit `5d757b4aafac546808df654d0b33423d179a3929` 進入 `main`，所有遠端與本機分支均保留；合併後 main run `36387141160` 的 backend、frontend、mysql-integration、browser-integration 全綠。PR-MVP-1 完成。

## Step MVP-03：成本引擎與無副作用試算 API

### 這一步在做什麼

像把兩台透明計算機接到同一份唯讀庫存快照：一台依最早批次逐層取用，另一台依剩餘數量計算權重；兩台同時回報結果，但都沒有改寫庫存的能力。

### 專業意義

將 Decimal 計算抽成不依賴 FastAPI 或 SQLAlchemy 的 pure module，可用固定輸入直接證明算法。HTTP service 只有唯讀 repository call，真實 MySQL test 再比較試算前後完整 row snapshot，避免只靠程式宣稱「沒有扣庫存」。

### 為什麼現在做

PR-MVP-1 已建立可持久化的 Product 與 PurchaseBatch；本步在不擴充 schema 的前提下完成面試核心價值，下一支 PR 才能安全地專注比較畫面與端到端展示。

### 執行前狀態

- 分支：`feat/interview-cost-simulation`。
- 起點：乾淨且與遠端一致的 `main` commit `5d757b4`。
- PR #15 已一般 merge；合併後 main CI run `36387141160` 四項全綠。
- 持久化 schema 只有 `products`、`purchase_batches` 與 Alembic version；沒有 order 或 simulation history。

### 已確認規則

- FIFO 依 `purchased_at ASC, batch_id ASC`，略過零剩餘量，可跨批並在不足時整體失敗。
- 加權平均使用剩餘數量權重，不是批次單價簡單平均。
- Python 全程使用 Decimal；中間結果不先 round，response 邊界才以 `ROUND_HALF_UP` 顯示兩位。
- 同一 response 並列兩種方法及客觀差額方向；相同時方向為 `equal`，不構成推薦。
- 試算只讀、不保存、不建立訂單，不修改 Product 或 PurchaseBatch。

### 計畫

- 先建立 1／25／30／31 個、同時間排序、十次重跑與 rounding 的 executable acceptance tests。
- 實作 framework-independent cost engine，再建立 simulation service、schemas、dependency 與 router。
- 用 API tests 固定字串金額、安全錯誤 envelope 與 CAD／正數 validation。
- 用隔離 MySQL 前後完整 row snapshot 與 table inventory 證明無副作用。

### 實際修改

- `app/costing/engine.py`：不可變 input/result dataclasses、FIFO、數量加權平均、營收／毛利／毛利率及絕對差額方向。
- `app/simulations/service.py`：只呼叫 `get_inventory`，將 ORM batch 映射至 pure input，不執行 add、flush、commit 或 update。
- `app/simulations/schemas.py`：正整數、正 Decimal、CAD-only request；所有金額與百分比在 response 邊界以字串兩位輸出。
- `app/simulations/router.py`：新增 `POST /api/v1/simulations/cost`，商品不存在與庫存不足沿用安全 error envelope。
- pure/service/API tests：固定 golden cases、同時刻 batch ID 次序、零庫存批次、簡單平均反例、十次 deterministic、無 mutation、round half up 與 validation。
- MySQL integration：連續十次試算、剛好 30、超量 31，並比對完整批次 row snapshot 及資料表集合。
- README 與 API 合約：補上試算端點、無副作用／不推薦說明，以及差額相等時的明確語意。

### 資料庫 migration

無。此 PR 刻意不新增資料表或欄位；新增 simulation/order/history schema 反而違反 MVP 的無持久化規則。

### 執行指令

- Targeted pytest：先執行三個新 test modules，確認 `app.costing` 不存在而產生 3 個預期 collection errors。
- 實作後重跑 targeted pytest、完整 backend pytest、Ruff lint／format 與 `alembic heads`。
- Frontend 雖無功能修改，仍執行 Oxlint、TypeScript、Vitest、production build 與 repository secret/artifact heuristic。
- 真實 MySQL 與 Playwright 將由 PR CI 的隔離環境執行；skipped local integration 不列為通過。

### 驗證結果

- 預期紅燈：3 個 collection errors，原因是 `app.costing` 尚不存在。
- 第一輪實作：12 passed、1 failed；失敗精確指出 recurring Decimal 被由 total 再除 quantity，造成最後一位中間精度漂移。
- 修正為加權單位成本只計算一次並沿用後，targeted tests 13 passed、0 failed、1 個既有 warning。
- 加入明確 `ROUND_HALF_UP` 邊界與 1 個商品完整顯示案例後，完整 backend：39 passed、0 failed、3 skipped、1 warning；三個 skip 均為未在本機啟用的隔離 MySQL tests。
- Ruff：45 files lint／format passed；Alembic head 維持 `20260928_01_inventory`。
- Frontend regression：10 passed；Oxlint、TypeScript、build 通過，21 modules；repository artifact／heuristic secret scan 通過。

### 失敗與修正

- Targeted 首輪揭露加權總成本乘上數量後，再反除數量重建單位成本，會因 Decimal context 對循環小數產生最末位差異。引擎改為只計算一次 `inventory_cost / available` 並把該精確中間值直接帶入 result；顯示值仍只在 API 邊界 round。
- Ruff 發現一個 import block 排序及三個格式差異；只以 Ruff 做機械修正後重新以 check-only 驗證。
- 嘗試啟動本機隔離 MySQL 時，WSL `docker` 不存在；依 README 改用 `docker.exe` 後，Docker Desktop Linux engine pipe 也未啟動。兩次均在建立 container 前失敗，沒有刪除或修改 volume；因此本機 integration 維持未通過，交由 PR CI 真實執行後再判定。

### 我在面試時可以怎麼解釋

- 計算引擎不需要 web server 或 database 就能測，這讓算法錯誤與整合錯誤可以分開定位。
- 加權平均保留原始 Decimal 中間值，`86.67` 只是顯示，不會拿顯示後數字繼續算總成本。
- 無副作用不只靠 code review：integration test 會把完整 MySQL rows 在十次 API 呼叫前後逐欄比較。

### 風險與未完成

此 PR 不做比較 UI、正式訂單、扣庫存、auth、匯率或任何新 schema。真實 MySQL 無副作用與 browser regression 尚待 PR CI 執行。

### 狀態與證據信心

本機 pure/service/API/regression 與品質檢查完成；CI 前信心 94/100，扣分是 MySQL snapshot test 尚未在乾淨 CI runner 執行，且最終比較 UI 屬下一支 PR。
