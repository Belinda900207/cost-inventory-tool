# Auth 邊界（待第二階段決策）

目前不提供任何登入端點、帳號或認證儲存。空 router 保留 `/api/v1/auth` 命名空間；呼叫 login/me 目前為 404，不是假成功。未配置 service 的保護 dependency 回 501，不能放行。

## 擬議合約，尚未上線

| 方法／路徑 | 輸入 | 成功 | 失敗 |
| --- | --- | --- | --- |
| POST /api/v1/auth/login | identifier、password（SecretStr） | 已驗證 Principal；session 建立方式待決定 | 401 統一安全訊息；422 安全驗證錯誤 |
| GET /api/v1/auth/me | 待選定的 session credential | subject、display_name | 401 未認證 |

Principal 是介面資料型別，不是 users table；subject 是未來身分來源提供的穩定識別字。LoginRequest 不限制 identifier 為 email，以免提前決定登入方式。

- 後端：schemas 描述 DTO；service Protocol 描述認證與解析身分能力；dependencies 先拒絕未配置狀態；router 無實作端點。
- 前端：features/auth/contracts.ts 定義型別與保留路徑，沒有登入 UI、storage 或假帳號。
- 第二階段需本人決定：身分供應者或本地帳密、角色權限、session/cookie/token 與 CSRF 策略、登出/逾時/撤銷、密碼重設及安全需求。不得直接採 JWT/localStorage。
- health 是公開運維介面，不包含使用者資料；正式保護路由將注入 require_principal。
