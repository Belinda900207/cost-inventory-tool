// Proposed contracts only; no login flow, session storage or fake principal.
export interface LoginRequest { identifier: string; password: string }
export interface Principal { subject: string; display_name: string }
export type AuthState = { kind: 'unconfigured' } | { kind: 'anonymous' } |
  { kind: 'authenticated'; principal: Principal }
export const plannedAuthRoutes = {
  login: '/api/v1/auth/login',
  me: '/api/v1/auth/me',
} as const
