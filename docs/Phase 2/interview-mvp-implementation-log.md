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
- commit、PR 與 CI 指令會在完成後繼續補記。

### 驗證結果

- 12 個 README 文件連結目的檔全部存在。
- 七份 Phase 1 文件全部 byte-identical。
- `git diff --check` 通過；backend、frontend、migration 路徑沒有修改。
- Backend Ruff：22 files passed；Alembic heads 成功且仍無 revision。
- Backend pytest：18 passed、0 failed、1 skipped、1 warning；skip 是未啟用的隔離 MySQL integration，沒有冒稱通過。
- Frontend Oxlint、TypeScript 與 production build 通過；Vitest 7 passed、0 failed。
- 暫存區共 13 個結果路徑：README、七個 R100 rename、五份新文件；493 insertions、8 deletions。
- cached whitespace、禁止的 env／產物路徑及強秘密模式檢查全部無命中。
- PR CI 尚未建立，因此 MySQL integration 與 Playwright 仍待遠端實跑。

### 失敗與修正

無本 PR 引入的失敗。pytest 保留既有 Starlette/httpx deprecation warning，沒有為文件 PR 升級相依套件或壓制警告。

### 我在面試時可以怎麼解釋

- 我先把 MVP-only 與正式版本邊界寫清楚，避免展示版被誤認為可公開部署。
- 每個需求都有後續 API、資料模型或測試證據。
- 計算精度與差額方向先寫成合約，前後端才不會各自解讀。

### 風險與未完成

PR-MVP-0 不含任何業務實作；功能仍須由後三支 PR 完成。

### 狀態與證據信心

本機文件與既有品質檢查完成；待精確 staging、commit、PR CI 與合併證據。現階段信心 95/100，扣分是遠端 MySQL／browser jobs 尚未對本分支實跑。
