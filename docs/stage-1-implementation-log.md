# 第一階段實作紀錄

本輪日期：2026-09-24。第一階段目標：可重建、可測試、可協作的工程骨架，不加入業務資料表或正式 auth。
目前僅接手 `test/health-checks`；第一階段仍進行中，不能宣稱完成。

## Step 00：接手與安全稽核

### 目的
核對真實狀態，保留使用者修改，限定本分支只改善既有 health 測試。

### 執行前狀態
- 使用者提供、待驗證：GitHub default branch 已為 main、先前 MySQL/前後端啟動成功、pytest 2 passed / 1 warning、前端 lint/build 通過。
- 初次讀取附件前只簡述讀取規格，尚未取得逐步規則；曾執行 `pwd`、初步 `rg --files` 及 `cat` 使用者附件，未修改檔案。

### 計畫
唯讀核對 Git、目錄、設定、工具，建立缺口表。只新增本紀錄，不改功能、不啟停服務、不連 DB。

### 執行指令
```bash
pwd
git status --short --branch
git branch -vv
git diff
git diff --cached
git ls-files
rg --files --hidden -g '!.git/**' -g '!**/node_modules/**' -g '!**/.venv/**' -g '!**/dist/**' -g '!**/.env' -g '!**/.env.*' -g '!**/__pycache__/**'
git --version
node --version
npm --version
python3 --version
backend/.venv/bin/python --version
docker --version
docker compose version
docker compose ps
git symbolic-ref refs/remotes/origin/HEAD
backend/.venv/bin/python -m pip show fastapi starlette httpx httpx2 ruff pytest sqlalchemy alembic
command -v ruff
ls -la docs scripts .agents .codex
git log -4 --oneline
```
另以 Python pathlib 讀取 `.gitignore`、`.env.example`、`.editorconfig`、`.nvmrc`、compose、backend requirements/app/Alembic、frontend package/Vite/App/Oxlint/tsconfig/README；搜尋 repository 與父路徑 AGENTS.md，未發現。使用 subprocess 執行 `git remote -v`，輸出前遮蔽 HTTPS userinfo；對根目錄、backend、frontend 的 `.env` 僅檢查存在與 `git check-ignore`，不讀 value。檢查 tracked 路徑是否含 `.env`、`.venv`、node_modules、dist。

### 指令說明
`--short --branch` 顯示精簡狀態與分支；`-vv` 顯示追蹤關係；`--cached` 檢查暫存修改。rg 排除套件、秘密及 Git 內部。`pip show` 只查已安裝版本，沒有安裝。`compose ps` 只查容器狀態。無遠端 Git 讀寫；官方文件查閱會接觸公開網站。

### 修改檔案
- `docs/stage-1-implementation-log.md`：新增本次稽核與逐步紀錄。
- `backend/tests/test_health.py`：使用者既有修改，這一步未變更。

### 實際結果與證據
- Git/read wrapper commands exit 0；注意多命令最後 exit 0 不代表每個子指令成功。
- 路徑 `/home/gunter/projects/cost-inventory-tool`，不在 `/mnt/c`。
- 分支 `test/health-checks`，HEAD `4853dbc`，無 upstream；本機 main 同 SHA 且追蹤 origin/main。
- 僅 test_health.py 未提交；staged diff 空。兩個測試精確檢查成功 JSON/200 與安全失敗 JSON/503，mock 呼叫次數也有檢查，檔尾缺 newline。
- origin 指向 GitHub Belinda900207/cost-inventory-tool；未連遠端核實 default branch。
- Git 2.53.0、Node v24.21.0、npm 11.19.0、Python（系統/venv）3.14.4。
- FastAPI 0.141.1、Starlette 1.7.0、httpx 0.28.1、pytest 9.1.1、SQLAlchemy 2.0.54、Alembic 1.20.0。
- 無 pyproject/Ruff config，requirements 固定版本但未含 Ruff；PATH 也沒有 Ruff。前端有 package-lock，lint=oxlint，build=tsc -b && vite build，沒有 test script。
- docs/scripts 為空，無根 README、.github/workflows。Alembic target_metadata=None，URL 為模板值。
- `.env` 存在且被 ignore，backend/frontend .env 不存在但符合 ignore；未追蹤上述秘密/產物路徑。

### 問題、Warning 與處理
- Docker：`The command 'docker' could not be found in this WSL 2 distro.`，未取得版本/容器健康證據，不嘗試啟停或變更 Desktop 設定。
- `fatal: ref refs/remotes/origin/HEAD is not a symbolic ref`；default branch 仍是使用者提供、待驗證。
- pip cache 目錄不可寫而停用 cache；查詢仍完成。`Package(s) not found: httpx2, ruff`。不安裝、不改 lockfile。
- compose healthcheck 以 `-p$$MYSQL_ROOT_PASSWORD` 傳密碼，有程序參數曝露風險；後續 DB 分支修正。
- 前端使用 Oxlint 而非需求 ESLint，留待 CI 分支決策。
- 已查閱 Starlette release-notes URL，但工具回 Internal Error，不能作為相容性/遷移依據。不更換 httpx。

### 官方學習資源
查閱日期均為 2026-09-24：
- Git status：https://git-scm.com/docs/git-status — 區分工作樹與 staged 狀態。
- Ruff linter：https://docs.astral.sh/ruff/linter/ — `ruff check` 檢查用途；本機尚未安裝。
- Ruff formatter：https://docs.astral.sh/ruff/formatter/ — `format --check` 僅檢查，不自動改檔。

### 狀態
部分完成：repository 稽核完成，Docker/default branch 等環境與遠端證據仍缺。

## P1-00～P1-11 稽核表（本輪，非最終驗收）

| 任務 | 狀態 | 證據 | 缺口 | 建議分支 |
| --- | --- | --- | --- | --- |
| P1-00 環境 | 部分完成 | Linux 路徑、Git/Node/npm/Python 版本 | Docker 不可用、clean clone 未驗證 | test/stage-1-verification |
| P1-01 協作 | 部分完成 | main 追蹤 origin/main、工作分支、ignore | default branch 遠端證據、PR template、完整 PR 流程 | ci/quality-gates |
| P1-02 MySQL | 部分完成 | mysql:8.4、named volume、app_user 範例 | 健康狀態、實際 app user SELECT 1、測試隔離、healthcheck 秘密 | chore/mysql-testing |
| P1-03 health | 部分完成 | summary route、DB layer SELECT 1 | live/ready/schema/router/dependency | feat/backend-health |
| P1-04 測試 | 部分完成 | 本輪兩個精確 mock API tests 與 tests 範圍 Ruff 通過 | 全後端既有 Ruff 問題、integration/request ID/smoke | test/health-checks；後續測試分支 |
| P1-05 Alembic | 部分完成 | migrations 模板與 ini | Settings/Base/metadata 接線與載入驗證 | chore/alembic-config |
| P1-06 前端 | 部分完成 | React/TS/Vite、/api proxy | 狀態頁/API client/型別/測試，仍為 counter | feat/frontend-health |
| P1-07 可觀測性 | 未完成 | 無對應模組 | request ID/logging/error envelope | feat/api-observability |
| P1-08 auth 邊界 | 未完成 | 無 auth 模組 | 僅模組邊界與延後決策文件 | chore/auth-skeleton |
| P1-09 CI | 未完成 | 無 .github | backend/frontend jobs、MySQL service、遠端實跑 | ci/quality-gates |
| P1-10 文件 | 部分完成 | 本紀錄；frontend 模板 README | 根 README、architecture/decisions/workflow/AI/verification | docs/stage-1-handoff |
| P1-11 最終驗收 | 未完成 | 無 clone/smoke 證據 | 全部重建與狀態切換驗證 | test/stage-1-verification |

## 後續順序（尚未授權建分支）
先完成本分支可用的驗證並呈現 diff，再等待使用者決定 Git 操作。
沿用規格順序：backend-health → api-observability → mysql-testing → alembic-config → frontend-health → auth-skeleton → quality-gates → stage-1-handoff → stage-1-verification。
health 先建立可替換 DB 邊界，observability 再補 ready 的一致錯誤格式；前兩支完成前 P1-03 不算完整驗收。每支開始前確認最新 main，分支切換/建立、套件安裝、lockfile、migration、Git 寫入均需先取得使用者同意。

## Step 01：目前 health-check 分支驗證

### 目的
重驗使用者的精確測試與現有前端品質，不將功能擴充混入本分支。

### 執行前狀態
test/health-checks；使用者 test_health.py 修改保留。Step 00 文件已新增。Ruff 未安裝。

### 計畫
只補測試檔最後換行；跑 Ruff、pytest、現有前端 scripts、diff/秘密檢查。沒有套件安裝、lockfile 修改、Git 寫入或 DB 操作。

### 執行指令
```bash
# repository root：透過 Python Path.read_bytes/write_bytes，僅在缺少時補一個 LF
# backend 工作目錄
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m pytest -q
# frontend 工作目錄
npm run lint && npm run build
# repository root
git diff --check
git status --short --branch
git diff --stat
git check-ignore .env backend/.venv frontend/node_modules frontend/dist
# pytest 卡住後的診斷
ps -eo pid,ppid,etime,args | rg '[p]ytest|[p]ython -m pytest'
# backend 工作目錄，沙箱內
timeout -s INT -k 5s 20s .venv/bin/python -m pytest -vv -o faulthandler_timeout=10
# backend 工作目錄，經 require_escalated 流程後於沙箱外
timeout -s INT -k 5s 30s .venv/bin/python -m pytest -q
```
另外以 Python 掃描 `git ls-files -co --exclude-standard` 列出的檔案，檢查 private-key header、GitHub token、AWS access key、含帳密的 URL 模式；只印檔案及模式名稱，不印命中值。

### 指令說明
`python -m` 確保使用指定 venv。Ruff 沒有 `--fix`；format 帶 `--check`。pytest `-q` 精簡輸出，`-vv` 定位卡住的測試；faulthandler 10 秒印 stack。timeout 先送 INT，5 秒後仍未退出才終止本次測試程序。`npm run build` 實際先 `tsc -b` 再 Vite build。測試和 build 可產生已忽略快取/產物。

### 修改檔案
- `backend/tests/test_health.py`：本輪僅補最後 newline；兩個測試邏輯全部為使用者既有變更。
- `docs/stage-1-implementation-log.md`：即時補上結果、風險、後續交接。
- 未新增刪除其他 source、修改套件或 lockfile。frontend/dist 與快取為被忽略的驗證產物。

### 實際結果與證據
- 補 newline：exit 0；Ruff lint/format 各 exit 1：`No module named ruff`。
- 第一次 pytest 在 sandbox 卡住，透過該工具 session 送 Ctrl-C 結束，exit 130，未停止使用者服務。
- 有時限診斷收集到 2 tests，卡在第一個 fixture 的 `TestClient.__enter__` → AnyIO `start_task_soon` → future/thread wait；尚未發送 /health request。timeout 最終 exit 137。
- 經權限流程於 sandbox 外重跑：exit 0，`2 passed, 1 warning in 0.23s`。支持 sandbox 執行環境相關問題，但未證明底層具體限制。
- `npm run lint && npm run build` exit 0；Oxlint 通過，TypeScript build check 通過，Vite 8.3.0 build 通過（20 modules）。没有 frontend test script，未宣稱 frontend tests 通過。
- diff check/status/stat/ignore 連續指令 exit 0；test diff 為 40 insertions、5 deletions（含使用者變更），新增紀錄尚未追蹤故未包含於 diff stat。
- 秘密啟發式檢查 exit 0，唯一命中 backend/alembic.ini 的模板 `driver://user:pass@localhost/dbname`，並非真實 credential；不能保證涵蓋所有秘密格式或 Git 歷史。
- `.env`、backend/.venv、frontend/node_modules、frontend/dist 均符合 ignore；無上述已追蹤產物。

### 問題、Warning 與處理
- 原文：`StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.`
- 已確認 FastAPI/Starlette/httpx 實際版本（Step 00），但官方 release page 讀取失敗，相容矩陣與遷移方案尚未確認；未安裝 httpx2、未壓制 warning。留待獨立相依性決策。
- ps 在隔離環境僅顯示該次 shell wrapper，無助確認另一 session；不再擴大列出程序。使用 session 控制停止自己的測試。
- Ruff 無法執行屬缺少工具，不是 lint 通過。安裝須符合使用者規格 §5.2 的明確同意；本輪不自行安裝。
- Docker 不可用、GitHub default branch 待遠端證據；沒有 integration、CI、smoke 或 clean clone 驗收結果。

### 官方學習資源
2026-09-24 查閱的 Ruff linter/formatter 官方頁見 Step 00，支持 check 與 format --check 的非自動修正模式。Starlette 遷移依據仍待查證，不能僅依 warning 文字作套件變更。

### 狀態
部分完成：pytest、前端現有 lint/type/build、diff/ignore 檢查通過；Ruff 受阻。不得建議合併。

## 本輪交接（不是第一階段最終報告）

- 現行資料流：React 仍為 Vite counter；Vite 已設定 /api proxy，但頁面尚未呼叫 health。FastAPI /health → check_database → SQLAlchemy SELECT 1；測試替換 check_database，不連 DB。
- 建議 commit message：`test: make health checks deterministic`。提交範圍為 test_health.py 與本紀錄；尚未 git add/commit/push/PR。
- 建議 PR title：`test: verify exact health success and failure responses`。
- 建議 PR body：
  - Why：既有測試同時接受 200/503，無法精確判斷成功與失敗合約。
  - What：以 mock 分別驗證 DB check 成功與失敗，斷言固定 JSON、HTTP status、呼叫次數及不洩漏原始錯誤；附稽核紀錄。
  - How to verify：backend `.venv/bin/python -m pytest -q`；安裝經批准 Ruff 後跑 lint/format；root `git diff --check`。
  - Evidence：pytest 2 passed/1 warning；frontend lint、tsc、build 通過。
  - Risks：Ruff 尚未通過、Starlette warning 未解、此 PR 只驗證 mock API，不能代表真實 MySQL 可用或整階段完成。
- Ruff 0.16.8 已獲使用者同意安裝到 backend/.venv，未改 requirements/lockfile；下一個必要人工決定是是否執行 git add/commit/push/PR。
- 不給第一階段最終完成度/信心百分比：本輪是初始稽核而非最終驗收，12 組任務均未全數達標；最終報告與量化評估待後續批准分支完成，避免用主觀權重冒充驗收結果。

## Step 02：安裝 Ruff 並取得後端品質基線

### 目的
補齊目前虛擬環境缺少的 Ruff，實際執行規格要求的 lint 與 format check。

### 執行前狀態
`backend/.venv` 未安裝 Ruff；requirements.txt 沒有 Ruff，repository 也沒有 pyproject.toml 或 Ruff 專用設定。工作樹仍只有使用者的 health 測試修改與本紀錄。

### 計畫
依使用者「繼續做」的明確同意，只在已被 Git ignore 的 backend/.venv 安裝 Ruff，不修改 requirements 或 lockfile。安裝後先檢查整個 backend，再依結果區分本分支與既有問題。

### 執行指令
```bash
git status --short --branch
git diff -- backend/tests/test_health.py
tail -100 docs/stage-1-implementation-log.md
cat backend/requirements.txt
cat .editorconfig
backend/.venv/bin/python -m pip --version
backend/.venv/bin/python -m pip install --no-cache-dir ruff
# 沙箱 DNS 失敗後，經 require_escalated 流程在沙箱外重跑相同安裝指令
backend/.venv/bin/python -m pip install --no-cache-dir ruff
# backend 工作目錄
.venv/bin/python -m ruff --version
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```
下載時間較長時，曾唯讀列出 `/tmp/pip-*` 內 Ruff wheel 的檔名與大小，確認由 4 MiB、5 MiB、7 MiB 持續增長；未讀內容或改檔。

### 指令說明
`--no-cache-dir` 不把下載包留在 pip cache；套件只進 backend/.venv。`ruff check` 執行 lint，`ruff format --check` 只比較格式、不改檔。第一次安裝在受限網路內失敗後，按權限規則重跑沙箱外版本。

### 修改檔案
- `backend/.venv`：安裝 Ruff 0.16.8；此目錄被 Git ignore。
- 沒有修改 requirements.txt、package-lock.json 或任何應用程式檔案。
- `docs/stage-1-implementation-log.md`：記錄本步驟。

### 實際結果與證據
- 沙箱內安裝 exit 1：無法解析 pypi.org，最後顯示找不到可用 distribution；這是網路解析失敗，不代表 Ruff 套件不存在。
- 沙箱外安裝 exit 0：下載 10.3 MB wheel，`Successfully installed ruff-0.16.8`。
- Ruff version exit 0：`ruff 0.16.8`。
- 全 backend lint exit 1：app/db.py、app/main.py、migrations/env.py 共 3 個 I001；app/main.py 有 1 個 BLE001。
- 全 backend format check exit 1：app/config.py、migrations/env.py 會被重新格式化；tests/test_health.py 的 fixture 簽名也需要格式調整。

### 問題、Warning 與處理
- 安裝在沙箱內遇到 `NameResolutionError`；依規則以同一指令要求沙箱外網路權限，成功完成。
- 其餘 Ruff 問題位於本分支未修改的 app/migration；不在 health 測試分支批次修正，避免混入功能與 migration 骨架整理。
- repository 沒有固定 Ruff 版本的開發相依設定，其他環境未必會取得相同版本；這是後續 quality-gates 工作的缺口。

### 官方學習資源
- Ruff Installing Ruff：https://docs.astral.sh/ruff/installation/（查閱日期 2026-09-24）— 支持以 pip 安裝與 `ruff` CLI 的使用方式；本專案實際安裝 0.16.8。
- Ruff linter／formatter 官方頁與用途見 Step 00。

### 狀態
完成：Ruff 已可執行，並取得可重現的全後端基線；全後端尚未通過。

## Step 03：只修正本分支測試格式並完成驗證

### 目的
讓本分支新增的 health 測試符合 Ruff，同時保留全後端既有問題的清楚邊界。

### 執行前狀態
Ruff 指出 tests/test_health.py fixture 函式簽名需換行；測試斷言與行為本身沒有 lint 問題。

### 計畫
只按 Ruff 格式調整 fixture 簽名，不改斷言；對 tests/ 與整個 backend 分別驗證，再重跑 pytest、前端檢查、diff 與秘密模式掃描。

### 執行指令
```bash
# apply_patch：只調整 tests/test_health.py fixture 簽名換行
# backend 工作目錄
.venv/bin/python -m ruff check tests
.venv/bin/python -m ruff format --check tests
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
# frontend 工作目錄
npm run lint
npm run build
# repository root
git diff --check
git status --short --branch
git diff --stat
# backend 工作目錄；已知 sandbox TestClient 卡點，經權限流程在 sandbox 外執行
timeout -s INT -k 5s 30s .venv/bin/python -m pytest -q
# repository root；只輸出命中檔名，不輸出匹配值
git ls-files -co --exclude-standard -z | xargs -0 -r rg -l --no-messages <秘密模式>
```

### 指令說明
tests/ 範圍證明本分支檔案合格；全 backend 檢查保留基線。pytest 仍有 30 秒上限。秘密掃描涵蓋 tracked 與未追蹤但未 ignore 的檔案，匹配 private-key header、常見 GitHub/AWS token 與含帳密 URL；屬啟發式檢查。

### 修改檔案
- `backend/tests/test_health.py`：將 fixture 參數與回傳型別依 Ruff 拆行；測試行為、精確 status/JSON 斷言與洩漏檢查不變。
- `docs/stage-1-implementation-log.md`：補記 Step 02、Step 03 與交接狀態。

### 實際結果與證據
- tests Ruff lint exit 0：`All checks passed!`。
- tests format check exit 0：`1 file already formatted`。
- 全 backend lint/format 仍各 exit 1；測試檔已不在問題清單，剩餘為 Step 02 列出的既有 app/migration 問題（format 問題降為 2 個）。
- pytest exit 0：`2 passed, 1 warning in 0.21s`。
- frontend lint/build exit 0：Oxlint、TypeScript、Vite 8.3.0 production build 通過，20 modules transformed。
- git diff --check exit 0；工作樹只有修改的 backend/tests/test_health.py 與未追蹤 docs/。
- 秘密模式掃描 exit 0，命中 backend/alembic.ini 的模板 credential URL，以及本紀錄對該模板的描述；未顯示值。沒有真實秘密證據，但啟發式掃描不是完整保證。

### 問題、Warning 與處理
- pytest 仍有同一個 StarletteDeprecationWarning；未在缺少官方相容性證據時更換 httpx 套件。
- 全後端 Ruff 尚未通過，因此這次結果只支持「本分支測試檔符合 Ruff」，不支持「整個後端品質閘門通過」。
- frontend 沒有 test script，本輪沒有前端功能測試結果。

### 官方學習資源
- Ruff linter：https://docs.astral.sh/ruff/linter/（查閱日期 2026-09-24）— 用於 tests 與全 backend lint。
- Ruff formatter：https://docs.astral.sh/ruff/formatter/（查閱日期 2026-09-24）— 用於只檢查格式。
- pytest output capture：https://docs.pytest.org/en/stable/how-to/capture-warnings.html（由測試輸出引用，查閱日期 2026-09-24）— warning 摘要位置；本輪未壓制 warning。

### 狀態
完成：目前分支的測試修改、tests Ruff、pytest、前端既有 lint/type/build、diff 與秘密模式檢查均已取得證據。全 backend 既有 Ruff 問題明確保留，需在後續相應分支處理。

## test/health-checks 分支收尾狀態

- 變更目的：把原本同時接受 200/503 的寬鬆測試，拆成 DB check 成功與失敗兩個精確案例。
- 修改內容：固定 HTTP status 與 JSON；驗證 DB check 呼叫一次；驗證失敗回應不洩漏原始 DB 例外；測試不連真實 DB。
- 驗證證據：tests Ruff lint/format 通過；pytest 2 passed/1 warning；前端既有 lint/type/build 通過；diff check 通過；秘密模式掃描只有已知模板/紀錄文字。
- 未完成風險：全 backend 既有 Ruff 失敗；Starlette/httpx warning 未解；Docker/DB integration、CI、smoke、clean clone 均不在本分支證據內。
- 建議 commit message：`test: make health checks deterministic`。
- 建議 PR title：`test: verify exact health success and failure responses`。
- 建議 PR 驗證：`cd backend && .venv/bin/python -m ruff check tests && .venv/bin/python -m ruff format --check tests && .venv/bin/python -m pytest -q`，再於 root 跑 `git diff --check`。
- Git 狀態：尚未 git add、commit、push 或建立 PR；依使用者規格在這些操作前停止。

## Step 04：確認 health-check 分支提交前狀態

### 目的
在任何 staging 前確認分支、工作樹與暫存區，確保本次 Git 收尾只處理 health 測試檔，docs/ 保持未追蹤。

### 執行前狀態
使用者明確授權只提交 `backend/tests/test_health.py`，並禁止 stage、commit、push 或刪除 docs/ 及其 Markdown。本輪禁止 push、PR 與 merge。

### 計畫
唯讀檢查目前分支、指定測試檔 diff 與 cached diff；若分支錯誤或暫存區已有內容就立即停止。

### 執行指令
```bash
git status --short --branch
git diff -- backend/tests/test_health.py
git diff --cached
```

### 指令說明
`status --short --branch` 同時顯示分支與精簡工作樹；指定 path 的 `git diff` 只讀取測試檔未暫存差異；`--cached` 檢查 index，沒有輸出表示暫存區為空。

### 修改檔案
- `docs/stage-1-implementation-log.md`：追加本步驟紀錄；保持 untracked，不加入暫存區。

### 實際結果與證據
- 指令組 exit 0。
- 分支為 `test/health-checks`。
- `backend/tests/test_health.py` 顯示預期修改；diff 為兩個精確成功／失敗測試與 fixture。
- `git diff --cached` 無輸出，暫存區原本為空。
- `docs/` 顯示 `?? docs/`，仍未追蹤。

### 問題、Warning 與處理
無。

### 官方學習資源
- Git status：https://git-scm.com/docs/git-status（查閱日期 2026-09-24）— 用於辨識工作樹與未追蹤檔案。
- Git diff：https://git-scm.com/docs/git-diff（查閱日期 2026-09-24）— 用於區分工作樹 diff 與 cached diff。

### 狀態
完成；條件符合，可以進入重新驗證。

## Step 05：提交前重新驗證 health 測試

### 目的
在 staging 前確認測試檔符合 Ruff、格式與測試要求，且工作樹 diff 沒有空白錯誤。

### 執行前狀態
分支與工作樹已在 Step 04 確認；暫存區為空，docs/ 未追蹤。

### 計畫
在 backend 執行 tests 範圍 Ruff 與 pytest，再於 repository root 執行 `git diff --check`。任一失敗就停止，不修改產品碼或相依套件。

### 執行指令
```bash
# backend 工作目錄
.venv/bin/python -m ruff check tests
.venv/bin/python -m ruff format --check tests
# 同一 pytest 指令經已核准的沙箱外環境執行，外層加 30 秒 timeout
.venv/bin/python -m pytest -q
# repository root
git diff --check
```

### 指令說明
Ruff `check` 執行 lint，`format --check` 只比較格式。pytest 執行兩個 health API 測試；因已知沙箱內 TestClient 卡點，於沙箱外執行相同測試。`git diff --check` 檢查未暫存差異的空白錯誤。

### 修改檔案
- `docs/stage-1-implementation-log.md`：追加驗證紀錄，保持 untracked。
- 測試與品質指令沒有修改原始碼；可能更新被 ignore 的快取。

### 實際結果與證據
- Ruff lint exit 0：`All checks passed!`。
- Ruff format check exit 0：`1 file already formatted`。
- pytest exit 0：`2 passed, 1 warning in 0.22s`。
- `git diff --check` exit 0，無輸出。

### 問題、Warning 與處理
- 已知 `StarletteDeprecationWarning`：Starlette TestClient 使用 httpx 已標記 deprecated。依使用者要求記錄但不安裝 httpx2、不升級套件。

### 官方學習資源
- Ruff linter／formatter 與 pytest 官方資源見 Step 03。
- Git diff：https://git-scm.com/docs/git-diff（查閱日期 2026-09-24）— `--check` 用於偵測 whitespace errors。

### 狀態
完成；所有指定檢查通過，可以精確 stage 測試檔。

## Step 06：精確加入 health 測試檔

### 目的
只把使用者允許的 `backend/tests/test_health.py` 加入 Git 暫存區，讓後續 commit 不包含 docs/ 或其他檔案。

### 執行前狀態
Step 04 已證明暫存區為空；Step 05 指定檢查全部通過；docs/ 未追蹤。

### 計畫
使用精確 pathspec 執行 `git add -- backend/tests/test_health.py`，不使用 `git add .`、`git add -A` 或資料夾路徑。

### 執行指令
```bash
git add -- backend/tests/test_health.py
# 沙箱內 .git 唯讀後，經 require_escalated 流程重跑完全相同的精確指令
git add -- backend/tests/test_health.py
```

### 指令說明
`--` 結束 Git 選項，後面只指定單一測試檔。這會更新 Git index，不會修改工作樹檔案或接觸遠端。

### 修改檔案
- Git index：只要求加入 `backend/tests/test_health.py`；實際內容會在下一步以 cached name/diff 核對。
- `docs/stage-1-implementation-log.md`：追加本步驟，保持 untracked，不 stage。

### 實際結果與證據
- 沙箱內第一次執行 exit 128：`Unable to create .git/index.lock: Read-only file system`，未完成 staging。
- 經權限流程重跑相同精確指令 exit 0。
- 未使用任何廣泛 add、commit、push 或刪除指令。

### 問題、Warning 與處理
沙箱不允許寫入 `.git/index.lock`；使用已獲授權的精確命令在權限流程下完成。是否確實只有一個 staged 檔案，必須由下一步 cached 檢查確認。

### 官方學習資源
- Git add：https://git-scm.com/docs/git-add（查閱日期 2026-09-24）— pathspec 可限制加入的檔案。

### 狀態
完成 staging 動作；等待暫存區核對，尚未 commit。

## Step 07：核對 health 測試暫存區

### 目的
在 commit 前證明 index 只包含允許的測試檔，docs/ 仍未追蹤，且 staged diff 沒有空白錯誤。

### 執行前狀態
已用精確 pathspec stage 測試檔；尚未 commit。

### 計畫
列出所有 cached 路徑、檢查 cached whitespace、閱讀指定測試 cached diff，最後查看精簡狀態。若 staged 路徑不只一個就停止。

### 執行指令
```bash
git diff --cached --name-only
git diff --cached --check
git diff --cached -- backend/tests/test_health.py
git status --short
```

### 指令說明
`--cached` 讀取 Git index 而不是未暫存工作樹；`--name-only` 便於精確比對路徑；`--check` 檢查即將提交 diff 的 whitespace errors。

### 修改檔案
- `docs/stage-1-implementation-log.md`：追加核對證據，保持 untracked。
- Git 唯讀檢查沒有修改 index 或工作樹。

### 實際結果與證據
- 指令組 exit 0。
- staged name-only 恰好一行：`backend/tests/test_health.py`。
- cached diff check 無輸出。
- cached diff 是預期 fixture、成功 200 與失敗 503 精確測試，包含不洩漏原始錯誤的斷言。
- status：`M  backend/tests/test_health.py`、`?? docs/`；沒有其他 staged 檔案。

### 問題、Warning 與處理
無。

### 官方學習資源
- Git diff：https://git-scm.com/docs/git-diff（查閱日期 2026-09-24）— cached diff 用於檢查 index 與 HEAD 的差異。

### 狀態
完成；暫存區符合使用者限制，可以建立指定 commit。

## Step 08：建立 health 測試 commit

### 目的
將 Step 07 已核對的唯一 staged 測試檔建立成本機 commit，不包含 docs/。

### 執行前狀態
Git index 只有 `backend/tests/test_health.py`；docs/ 顯示未追蹤；所有指定檢查通過。

### 計畫
使用使用者指定的 commit message 建立本機 commit，不使用 `-a`，不 push、不建立 PR。

### 執行指令
```bash
git commit -m "test: make health checks deterministic"
```

### 指令說明
`-m` 設定 commit subject；未使用 `-a`，因此只提交已核對的 index 內容。指令經權限流程寫入本機 `.git`，不接觸遠端。

### 修改檔案
- 本機 Git 歷史：新增一個 commit。
- `docs/stage-1-implementation-log.md`：追加結果，仍未追蹤且未包含在 commit。

### 實際結果與證據
- exit 0。
- short hash：`c86b609`。
- message：`test: make health checks deterministic`。
- Git 摘要：`1 file changed, 42 insertions(+), 5 deletions(-)`。

### 問題、Warning 與處理
無。commit 的精確檔案清單與最終狀態仍須由下一步查核。

### 官方學習資源
- Git commit：https://git-scm.com/docs/git-commit（查閱日期 2026-09-24）— commit 記錄目前 index 的內容。

### 狀態
完成；等待提交後查核。未 push、未建立 PR、未 merge。

## Step 09：提交後查核與停止點

### 目的
確認最新 commit 只包含允許的 health 測試檔，docs/ 仍留在本機未追蹤，然後依使用者要求停止。

### 執行前狀態
本機 commit `c86b609` 已建立；尚未 push、PR 或 merge。

### 計畫
讀取 HEAD 統計與最終精簡狀態；不再執行任何 Git 寫入或遠端操作。

### 執行指令
```bash
git show --stat --oneline --summary HEAD
git status --short --branch
```

### 指令說明
`git show --stat` 顯示 HEAD 的 subject 與檔案統計；`git status --short --branch` 顯示目前分支及未追蹤檔案。

### 修改檔案
- `docs/stage-1-implementation-log.md`：追加最終查核；仍為 untracked，未包含於 commit。
- 查核指令沒有修改 Git 或工作樹。

### 實際結果與證據
- 指令組 exit 0。
- HEAD：`c86b609 test: make health checks deterministic`。
- commit 只列出 `backend/tests/test_health.py`：42 insertions、5 deletions。
- 最終狀態：分支 `test/health-checks`，僅 `?? docs/`。
- docs/ 沒有 stage、commit 或刪除；其 Markdown 保留在本機。

### 問題、Warning 與處理
無。

### 官方學習資源
- Git show：https://git-scm.com/docs/git-show（查閱日期 2026-09-24）— 用於檢查 HEAD commit 內容與統計。

### 狀態
完成。本輪按要求停止；未 push、未建立 Pull Request、未 merge。

## Step 10：補記 GitHub 流程與重新接手
- 日期：2026-09-27；起始分支 test/health-checks，只有 docs/ 未追蹤；本機 main 4853dbc 落後遠端。
- 目的／範圍：保護既有紀錄，核實 PR #1，先以獨立文件 PR 納入版本管理。
- 方法與原因：原文保留為歷史；本輪使用者授權取代舊文「需逐項批准」限制。順序改為文件保存 → CI → 功能，確保後續 PR 有自動檢查。原檔實際只有 Step 00～09，本步補足 Step 10。
- 指令與用途：`git status --short --branch`、`git branch -vv`、`git log -3 --oneline`、`git remote -v`、`git ls-files`、`git diff` 唯讀稽核；`cp docs/stage-1-implementation-log.md /tmp/cost-inventory-stage-1-original.md` 保留原始副本；`gh pr view 1 --json number,state,mergeCommit,url,files,statusCheckRollup` 查遠端證據；`git fetch origin` 更新遠端參照、`git switch main`、`git merge --ff-only origin/main` 僅快轉同步，再建立 docs/preserve-stage-1-log。
- 修改：只追加本紀錄；未讀取 .env 值，未改使用者資料。
- 實際結果：gh 2.101.0 可查詢私人授權範圍；先前安裝／登入與 push 已由使用者提供，本輪未重新安裝或輸出憑證。PR #1 已 MERGED，僅 backend/tests/test_health.py，merge d5669d3f91a572247b032fd43a607d9eefb632a0；statusCheckRollup 為空，沒有 CI，不符合完整品質門檻。
- 問題：Docker 指令仍回 WSL integration 未啟用；真實 DB／重啟持久性驗收受阻，其他工作繼續。先前三份規格未附於本輪，以本輪完整要求為準。92% 為規劃信心，不是實作進度。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/1
- 官方來源：本步無新增技術引用，依實際 CLI 結果。
- 狀態：文件保存進行中；下一步 CI 基線。第一階段仍進行中。

## Step 11：CI 基線與版本固定
- 日期／分支：2026-09-27，ci/quality-gates；文件 PR #2 合併 bb6b1b6 後由乾淨 main 開分支。
- 目的：先讓 PR/main push 自動跑後端 tests Ruff/pytest 與前端 lint/typecheck/build，再擴到全後端。
- 方法：GitHub Actions 是每次推送觸發的獨立執行環境；以固定 Python 3.14.4、Node 24.21.0、Ruff 0.16.8 與既有 lockfile 降低漂移。保留既有 Oxlint，不並行引進重複 ESLint；tsc 負責型別檢查。
- 指令：`ruff check backend`、`ruff format --check backend` 確認既有 4 lint / 2 format 問題；`npm ci` 依 lockfile 安裝；pytest 與前端 checks 待下步實測。
- 修改：.github/workflows/quality.yml、backend/requirements-dev.txt、backend/pyproject.toml、frontend/package.json；明確專案 Ruff 規則，不依賴家目錄設定。
- 結果：文件 PR 已合併，CI 設定已建立，尚未宣稱遠端綠燈。
- 風險：保留 Starlette/httpx deprecation warning；全後端 Ruff 將於本 PR 修正後擴大。
- 證據：https://github.com/Belinda900207/cost-inventory-tool/pull/2
- 官方來源：2026-09-27 查閱 GitHub Actions 與 Ruff/Oxlint 官方搜尋；最終可追蹤依據為 workflow 及實跑結果。
- 任務狀態：文件保存已驗收；CI 進行中；其餘任務維持未驗收。
- CI 故障演練：暫時加入 test_ci_gate.py 的故意失敗，要求遠端 pytest 紅燈；修正 commit 移除此檔後才可合併，故障版本不得進 main。
- 官方依據（2026-09-27）：https://docs.github.com/en/actions/tutorials/build-and-test-code/python 、https://docs.astral.sh/ruff/configuration/ 、https://oxc.rs/docs/guide/usage/linter 。

## Step 12：驗證 CI 紅燈並擴大全後端門檻
- 日期／分支：2026-09-27，ci/quality-gates；PR #3 初版含明確故障探針。
- 目的與方法：先證明遠端 pytest 會拒絕失敗，再移除演練；修正 import/format，保留 /health 對任意 DB 例外安全 503 的原合約，以單行 BLE001 註解說明例外邊界。
- 指令：`gh pr checks 3` 查 checks；`gh run view 36255713755 --log-failed` 核對失敗原因；`ruff check backend --fix` 修 import；`ruff format backend` 修格式；backend `pytest -q tests/test_health.py`、全 Ruff；frontend `npm ci && npm run lint && npm run typecheck && npm run build`。
- 修改：app/config.py、app/db.py、app/main.py、migrations/env.py 只整理既有 lint/format；workflow 改檢查全 backend；移除本 PR 新增的故障 test_ci_gate.py。
- 本機結果：2 passed / 1 Starlette warning；全 Ruff 通過（含探針 7 files）；前端 npm ci 0 vulnerabilities、lint/typecheck/build 通過。
- 遠端結果：初次 run 36255713755 backend fail、frontend pass，修正後將重新驗證，不把本機結果當 CI。
- 風險：BLE001 例外僅 legacy health 邊界；後續拆分 router 時維持安全錯誤。CI 紅燈並不自動代表 GitHub branch protection 已配置，合併仍須逐次核對 checks。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/3 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36255713755
- 官方依據：沿用 Step 11。
- 狀態：CI 待修正後驗收；下一步後端健康 API。

## Step 13：後端健康檢查與設定邊界
- 日期／分支／前置：2026-09-27，feat/backend-health；PR #3 最新 CI 36255812580 全綠後合併 490ba80，main 同步乾淨。
- 目的：保留 /health 精確合約；新增不連 DB 的 live 與 SELECT 1 ready。
- 方法：router 拆分路由；Depends 提供可替換 callable，使單元測試不接觸使用者 DB；延後建立 settings/engine，使 live 不依賴 DB 設定。SecretStr 避免設定 repr 顯示密碼；URL.create 正確處理特殊字元，連線/讀寫/pool 有界逾時。
- 指令／用途：`ruff check backend --fix`、`ruff format backend` 整理；backend `pytest -q` 驗證成功/失敗/live/SELECT 1/密碼遮蔽；全 Ruff check/format check 核對。
- 修改：app/config.py、db.py、health.py、main.py；tests/test_health.py 改依賴注入測試，新增 test_db.py。
- 本機結果：7 passed，1 已知 Starlette warning；Ruff 全通過，8 files 格式通過；未連真實 DB。
- 問題／決策：舊 /health 失敗 body 不能任意加入 error 欄位；下一步只對新 /health/ready 與一般錯誤採 envelope，legacy 用 header 追蹤。官方 Starlette 現確認 httpx 仍受支援但 deprecated，本階段保留固定版本與顯示 warning，不盲目升級。
- 追蹤：CI 基線 https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36255812580 ；本主題 PR 建立後於驗收表彙整。
- 官方來源／日期：2026-09-27，https://fastapi.tiangolo.com/advanced/testing-dependencies/ 、https://docs.sqlalchemy.org/en/20/faq/connections.html 、https://starlette.dev/testclient/ 。
- 任務表：CI 基線已驗收（integration/frontend tests 待擴充）；health 本機已驗證、遠端待驗收；Docker 仍不可用；其他未開始。

## Step 14：安全 request ID、結構化 log 與 error envelope
- 日期／分支／起點：2026-09-27，feat/api-observability；PR #4 CI 36255985191 全綠，合併 d830837 後同步 main。
- 目的與方法：middleware 為 HTTP request 建立上下文；只接受單一 1–64 字元英數/底線/連字號 ID，其餘重生 UUID。response header 與 error body 共用 ID；一般 HTTP/validation/500 回安全 envelope。legacy /health 為相容性例外，body 不變。
- 指令：backend `pytest -q`、`ruff check .`、`ruff format --check .`；Git 指定路徑 add，列 staged filenames、diff check、秘密模式與完整 diff 審查後 commit/push。
- 修改：app/observability.py、main.py、health.py；tests/test_observability.py 與健康失敗斷言。
- 結果：14 passed / 1 已知 warning；全 lint/format 通過（10 files）。涵蓋非法/過長/重複 ID、ID 唯一、404/405/422/500、安全 log、舊 health、新 ready。
- 安全邊界：log 只含時間、level、service、environment、request_id、method、路由模板 path、status、duration_ms、固定 message；未知路徑用 <unmatched>。不記 query、body、例外 traceback 或完整 DB URL。啟動時需關閉 Uvicorn access log，README 將提供指令。
- 風險：此階段無 streaming API；若未來加入串流，需補 response 開始後例外策略。ENVIRONMENT 從程序環境讀取，預設 development。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/4 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36255985191
- 官方來源：沿用 FastAPI/Starlette 依賴文件；本步合約由本專案測試定義。
- 任務表：health 已驗收單元/API；observability 本機完成、CI 待驗收；DB integration 未開始；第一階段仍進行中。

## Step 15：隔離 MySQL 與安全 healthcheck
- 日期／分支／起點：2026-09-27，chore/mysql-testing；PR #5 CI 36256128550 通過，合併 7d06d90 後開始。
- 目的：開發與測試完全分離；真實 MySQL SELECT 1、重啟與故障恢復由 CI 驗證。
- 方法：獨立 compose.test.yaml 固定專案 cost-inventory-test、3307、test_app、cost_inventory_test、獨立 named volume；測試啟用旗標 RUN_MYSQL_INTEGRATION=1 並 assert 隔離設定，僅此 project 可 stop/restart。以 @@server_uuid 重啟不變驗證 datadir 持久性，不建立業務表或測試表。
- 指令：`python3 scripts/init_test_env.py` 以隨機密碼建立 mode 0600 .env.test，O_EXCL 避免覆寫；`bash -n scripts/mysql-healthcheck.sh` 語法檢查；backend pytest 與 Ruff。`docker version` 沙箱內外均仍顯示 WSL 未整合，使用者回覆 ok 後已重驗，未假定修好。
- 修改：compose.yaml 只綁 localhost 與改 app user healthcheck；新增測試 compose、healthcheck/init scripts、integration test；CI 新增 mysql-integration job 與 scripts Ruff。
- 安全：healthcheck 以 umask 077 的一次性 client option file 傳密碼，shell builtin 轉義反斜線/引號/換行；不以 -p 密碼 argv 或 deprecated MYSQL_PWD 傳遞，退出只清理自己建立的暫存檔。未更動 .env 或現有 volume。
- 結果：本機 14 passed / 1 skipped（integration opt-in）/ 1 warning；Ruff 12 files 通過，shell 語法通過；真實 DB 待 CI，本機 Docker 阻塞仍保留。
- 風險：MySQL image 固定 8.4 系列而非 digest，修補版會更新；volume 不刪除。測試 DB 重啟/中斷不代表已重啟使用者開發 DB。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/5
- 官方來源／日期：2026-09-27，https://docs.docker.com/reference/compose-file/services/ 、https://dev.mysql.com/doc/refman/8.4/en/mysql-command-options.html 、https://dev.mysql.com/doc/refman/8.4/en/environment-variables.html 。
- 任務表：observability 已驗收；MySQL 隔離程式完成、CI/本機待验收；其餘未開始。
- 補充相依：`pip install 'PyMySQL[rsa]==1.2.3'` 支援 MySQL 8.4 預設 caching_sha2_password 首次認證；新增固定 cffi 2.1.1、cryptography 50.0.1、pycparser 3.0，實際安裝成功。這些不是使用者帳密或 auth 業務功能。

## Step 16：Alembic 設定與空 metadata 接線
- 日期／分支／起點：2026-09-27，chore/alembic-config；PR #6 三項 CI 通過（36256317004），merge 5346f10，main 同步。
- 目的／方法：API 與 Alembic 共用 Settings URL 及 Base.metadata，URL 直接交 SQLAlchemy 避免 ini 百分號插值與明文憑證。保留 versions 目錄但不造空 revision、不 create_all。
- 指令：backend `pytest -q`、`alembic heads`、全 Ruff；integration 加入 subprocess `python -m alembic current`，沿用隔離 DB 環境，成功才繼續故障演練。
- 修改：app/db.py 的 DeclarativeBase；migrations/env.py/README/versions/.gitkeep；alembic.ini 移除模板 URL 並使用 %(here)s 路徑；tests/test_migrations.py、integration test。
- 結果：本機 15 passed、1 skipped、1 warning；13 files Ruff 通過；alembic heads exit 0 且無 revision。PR #6 的真實 MySQL CI 已完成 app SELECT 1、重啟持久性、outage/recovery；本機 Docker 仍無法執行。
- 問題／風險：alembic current 的本機真實 DB 證據待 Docker；遠端本 PR 將驗證。連線 SQLAlchemyError 轉為不帶原始資料的 CommandError；不印 credentials。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/6 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36256317004
- 官方來源／日期：2026-09-27，https://alembic.sqlalchemy.org/en/latest/tutorial.html 。
- 任務表：MySQL CI 已驗收／本機仍待驗收；Alembic 本機無 DB 檢查完成，真實連線待 CI；前端/auth/文件/clean clone 未開始。

## Step 17：React 服務狀態頁與前端測試
- 日期／分支／起點：2026-09-27，feat/frontend-health；PR #7 三項 CI 36256488044 通過，merge 9a4f105 後同步 main。
- 目的：以真實相對 API 取代 counter；顯示 loading/成功/DB unavailable/backend disconnected/未知狀態與重試。
- 方法：api/client 集中 fetch、10 秒 timeout、AbortSignal、JSON 合約驗證；元件卸載取消請求；Vite /api proxy 保留、target 改 127.0.0.1 避免 IPv6 localhost 差異。Vitest/jsdom/Testing Library 驗證使用者可見狀態，CI 新增 npm test。
- 指令：`npm view` 查版本；frontend `npm install --save-dev --save-exact vitest@5.0.2 @testing-library/react@16.3.3 jsdom@30.1.1`、`npm run lint && npm run typecheck && npm test && npm run build`。
- 修改：frontend App/CSS/index、api/client、App.test、vitest.config、tsconfig.node、package/lock、vite config；workflow 加測試。
- 實際結果：安裝 71 packages，0 vulnerabilities；7 tests passed（載入、成功相對 URL、DB 失敗/重試恢復、network 失敗、非 JSON、合約錯誤、卸載取消）；lint/tsc/build 通過，build 18 modules。
- 失敗紀錄：第一次誤在 repository root 跑 npm，ENOENT 因 root 無 package.json；改 frontend 工作目錄後成功，未改專案結構。
- 風險：目前元件測試 mock network，尚未代替瀏覽器→Vite→API→MySQL 最終驗收；預期 production 需同源反向代理，CD 不在本階段。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/7 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36256488044
- 官方來源／日期：2026-09-27，https://vitest.dev/config/environmentoptions 、https://playwright.dev/docs/test-webserver （用於規劃下一步 browser 驗收）。
- 任務表：Alembic CI 已驗收；前端本機完成/遠端待驗收；auth、交接文件、乾淨 clone 未完成。
- 信心評估：對「已實作 API/狀態頁邊界正確」信心 85/100，依據 API 15 tests、前端 7 tests 與前次真實 DB CI；扣分為 browser end-to-end 與本機 Docker 缺證據。這是信心而非實作完成度；下次以 clean clone/browser 證據提升。

## Step 18：Auth 模組介面與拒絕邊界
- 日期／分支／起點：2026-09-27，chore/auth-skeleton；PR #8 CI 36256692612 全綠，merge c651bae 後 main 同步。
- 目的：只預留 schema/service/dependency/router 與前端型別，不決定身分來源或 session 儲存。
- 方法：Protocol 定義能力而無實作；未配置 service 明確 501；空 router 不掛 login/me，實際 404。LoginRequest 的 password 使用 SecretStr。auth-contract 記錄擬議合約與本人待決策事項。
- 指令：backend pytest/Ruff；frontend lint/typecheck/test/build；Git 精確 stage/diff/秘密模式核對。
- 修改：backend/app/auth 模組、main router、auth boundary tests；frontend/features/auth/contracts、vite rewrite；docs/auth-contract.md。
- 結果：本機 backend 18 passed / 1 skipped / 1 warning，Ruff 19 files 通過；frontend 7 tests、lint/tsc/build 通過。
- 修正發現：原 Vite rewrite 刪除所有 /api，會把未來 /api/v1/auth 錯轉 /v1/auth；改為只移除 health 的開發 proxy 前綴，業務 /api/v1 保留。
- 風險：Principal 只是 DTO，無 users table、無假帳號、無 JWT/localStorage。身分驗證尚未實作，這是本階段要求的邊界。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/8 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36256692612
- 官方來源：沿用 FastAPI Depends 文件；未新增外部認證方案。
- 任務表：前端已通過 CI；auth 本機完成/遠端待驗收；文件與最終驗收未完成。
- 後续順序調整：先做 browser 驗收工具 PR，再整理 README／交接，讓 README 引用已實跑的命令；最後 clean clone 與 main 驗收單獨補證據。

## Step 19：瀏覽器端到端驗收工具與產物檢查
- 日期／分支／起點：2026-09-27，test/browser-verification；PR #9 三項 CI 36256859998 通過，merge 6e7a744 後同步 main。
- 目的：以 Chromium 實測 loading、成功、真實 DB 失敗／恢復與後端斷線；保留畫面 artifact，並檢查 Git 追蹤範圍與 bundle 秘密。
- 方法：Playwright 固定 1.63.0；Vite webServer 提供 UI。真實案例先確認 8000 未被其他程序占用，再由只讀 `.env.test` 的 helper 啟動 API；只停止固定 `cost-inventory-test` Compose project。測試 finally 恢復測試 DB，從不刪 volume。
- 指令／用途：`npm install --save-dev --save-exact @playwright/test@1.63.0` 更新 lockfile；`npx playwright install chromium` 下載瀏覽器；`npm run test:e2e` 執行；`python scripts/check_repository.py` 檢查 tracked env/產物與 production bundle。
- 修改：Playwright config/e2e、browser CI job、API helper、repository checker、package/lock、tsconfig、gitignore。CI 會安裝 Chromium system deps，跑真實 MySQL/browser 並上傳 14 天 screenshot evidence。
- 本機結果：npm audit 0 vulnerabilities；Oxlint、tsc、7 component tests、production build 18 modules、tracked artifact 與 bundle heuristic secret scan 通過。
- 失敗紀錄：本機 Playwright 兩案例在 browser launch 前因缺 `libnspr4.so` 失敗；`playwright install-deps chromium` 嘗試安裝，但 sudo 要求互動密碼而 exit 1。這不是 UI assertion 結果。本機 Docker 仍不可用，真實案例須由 CI 驗證。已把 opt-in skip 移到 test 宣告前，避免未啟用案例建立 browser fixture。
- 安全：checker 不讀開發 `.env`；只可讀自動生成 `.env.test` 的 password 值以比對 bundle，且不輸出值。API helper assert test DB 名稱／user／port，不接受開發 DB。
- 風險：CI browser job 尚待實跑；artifact 只保存 14 天，長期證據記錄 run URL 與摘要。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/9 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36256859998
- 官方來源／日期：2026-09-27，https://playwright.dev/docs/test-webserver 。
- 任務表：auth 已驗收；browser 工具本機部分完成／CI 待驗收；交接文件與 clean clone 未完成。

## Step 20：文件交接與可重建命令
- 日期／分支／起點：2026-09-27，docs/stage-1-handoff；PR #10 四項 CI run 36322992915 全綠，merge 61e56b1 後同步 main。
- 目的：把新開發者從 clone、設定、啟動、測試到 PR 的實際流程放進 repository；整理架構、決策、AI 協作與驗收證據。
- 方法：README 只列已由本機或乾淨 runner 執行過的命令；env 初始化使用 O_EXCL 與 0600 隨機值，既有 `.env` 不讀不覆寫。分離「已通過」「待 final main」「本機環境阻塞」，不把 CI 證據冒充本機 Docker。
- 指令：`gh run view 36322992915 --log` 篩選測試摘要；`gh run download ... browser-evidence` 下載 artifact 到 `/tmp`；逐張檢查 healthy、DB unavailable、backend unavailable、loading；本步將重跑 Ruff、pytest、前端完整檢查、link/秘密/diff 檢查。
- 修改：根 README；architecture/decisions/development-workflow/ai-workflow/stage-1-verification；PR template；scripts/init_dev_env.py；補 `.env.example` 欄位。
- 實際結果：PR #10 browser 2 passed / 15.9s；mysql log 明確顯示 Alembic current 成功與 MySQL 8.4 app SELECT 1、persistent UUID、outage/recovery；四張 PNG 均存在且人工檢查文字／狀態正確。交接後本機 backend 18 passed／1 integration skipped／1 warning、Ruff 22 files、Alembic heads 通過；frontend 7 passed、lint/typecheck/build（18 modules）與 2 e2e cases discovery 通過；repository/bundle scan 與 diff check 通過。init_dev_env 在既有 `.env` 上只回報 preserved，前後 mtime/size 完全相同。
- 問題／風險：browser artifact retention 14 天；文件保存永久 run URL 與摘要。本機 WSL Docker 仍不可用。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/pull/10 、https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36322992915
- 官方來源：先前各步所列官方文件；本步以 repository 實際命令與 CI 證據為主。
- 任務表：CI/health/observability/MySQL/Alembic/frontend/auth/browser 已驗收；文件進行中；clean clone 與 main push 最終驗收未完成。

## Step 21：Clean clone、本機 MySQL 與 main 最終驗收
- 日期／分支／起點：2026-09-27，test/stage-1-verification；PR #11 四項 CI run 36323359476 通過，merge 22e87b5 後同步 main。
- 目的：依 README 從遠端 main 全新重建，補本機真實 DB 證據，並核對合併後 main push CI。
- 方法：`mktemp -d` 建全新 `/tmp/cost-inventory-clean-zI2ddv`，clone `main`；不複製現有 venv/node_modules/env。依 README 建 venv、pip install requirements-dev、npm ci、init_dev_env，再執行後端／前端／產物檢查。本機只啟動 `cost-inventory-test`，不操作開發 Compose。
- 指令／用途：`git clone --branch main --single-branch ...`；README 安裝與測試命令；`gh run list --branch main --workflow 'Quality gates'`；Windows `docker.exe version` 與固定 test Compose；以 `/tmp/cost-inventory-docker-bin/docker` 暫存 wrapper 讓 integration subprocess 使用同一 Docker CLI；完成後 `docker.exe compose ... stop`，沒有 down 或刪 volume。
- Clean clone 結果：HEAD `22e87b54...`、初始 status clean；npm ci 101 packages／0 vulnerabilities；新 `.env` mode 600 且 ignored；backend 18 passed／1 integration skipped／1 warning，Ruff 22 files、Alembic heads 通過；frontend 7 passed、lint/typecheck/build 18 modules、2 e2e cases discovery、bundle/repository scan 通過。
- 本機 DB 結果：原生 `docker` 仍顯示 WSL integration 未啟用；直接 `docker.exe` 在 Docker Desktop 啟動後取得 server 29.8.0。隔離 MySQL 測試 1 passed／1 warning／19.93s，log 證明 Alembic current、MySQL 8.4 app SELECT 1、server UUID 持久、DB stop 時 live 200／ready 503、恢復後 ready 200。測試 DB 最後 stopped，volume 保留；開發 DB 未啟動、停止或修改。
- main 證據：push run 36323469957 對 `22e87b5` completed success，backend/frontend/mysql-integration/browser-integration 四項全綠。PR #11 run 36323359476 亦四項全綠。
- 問題／風險：Playwright 本機 Linux Chromium 仍缺系統 library 且自動 install-deps 需要互動 sudo；同一 clean checkout 的 GitHub browser job 已安裝依賴並通過。WSL native docker integration 建議由本人於 Desktop 設定修復，README 補 `docker.exe` fallback。Starlette/httpx warning 保留為已知技術債。
- 追蹤：https://github.com/Belinda900207/cost-inventory-tool/actions/runs/36323469957 、https://github.com/Belinda900207/cost-inventory-tool/pull/11
- 任務表：第一階段必要項全部已驗收；本機環境限制與第二階段待決策已明列。
- 信心評估：第一階段實作 98/100；支持為 clean clone、PR/main 四層 CI、本機與 CI 雙重 DB 故障證據、browser artifacts、秘密/產物檢查。扣 2 分為 WSL native docker symlink 與已知 TestClient deprecation warning。此值是證據信心，不是完成度；驗收項本身已全部完成。
