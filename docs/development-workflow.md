# 開發與 PR 流程

1. 從最新 `main` 建立單一目的短分支。
2. 先讀 `git status --short --branch`，保留所有既有修改；不用 `git reset --hard`、`git clean -fd`、force push 或廣泛 `git add .`。
3. 每個有意義步驟更新 `stage-1-implementation-log.md`：目的、方法、命令、結果、失敗、風險與連結。
4. 執行與變更相稱的本機檢查。DB 故障測試只可使用 `cost-inventory-test`。
5. 以精確 pathspec stage；提交前列 staged filenames、跑 `git diff --cached --check`、審查完整 diff 與秘密模式。
6. PR 描述包含 Why、What、How to verify、Risks／boundaries、Evidence，分開列本機與 CI 結果。
7. 等所有適用 checks 全綠，核對 PR files 後合併；同步 `main` 再開下一支。

第一階段必要 checks：backend Ruff/pytest、frontend Oxlint/TypeScript/Vitest/build/bundle check、真實 MySQL integration、Playwright browser integration。不得以「本機成功」代替 CI，也不得把 skipped integration 稱為通過。

若 Docker 不可用，仍可完成單元、API mock、前端與文件；清楚標示本機 integration 缺證據，使用乾淨 GitHub runner 補驗。不可為了繞過限制而操作開發 DB 或刪 volume。
