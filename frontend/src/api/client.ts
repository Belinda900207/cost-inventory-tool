export type HealthState =
  | { kind: 'loading' }
  | { kind: 'healthy' }
  | { kind: 'database-unavailable'; requestId?: string }
  | { kind: 'backend-unavailable' }
  | { kind: 'unexpected'; requestId?: string }

async function probe(path: string, signal: AbortSignal) {
  const response = await fetch(`/api/health/${path}`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]),
    headers: { Accept: 'application/json' },
    cache: 'no-store',
  })
  const body: unknown = await response.json()
  const header = response.headers.get('x-request-id')
  const requestId = header && /^[A-Za-z0-9_-]{1,64}$/.test(header) ? header : undefined
  return { response, body, requestId }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

export async function getHealth(signal: AbortSignal): Promise<HealthState> {
  const [live, ready] = await Promise.allSettled([probe('live', signal), probe('ready', signal)])
  if (live.status === 'rejected' || !live.value.response.ok ||
      !isRecord(live.value.body) || live.value.body.status !== 'ok') {
    return { kind: 'backend-unavailable' }
  }
  if (ready.status === 'rejected') return { kind: 'unexpected' }
  const { response, body, requestId } = ready.value
  if (response.ok && isRecord(body) && body.status === 'ok' && body.database === 'ok') {
    return { kind: 'healthy' }
  }
  if (response.status === 503 && isRecord(body) && isRecord(body.error) &&
      body.error.code === 'database_unavailable') {
    return { kind: 'database-unavailable', requestId }
  }
  return { kind: 'unexpected', requestId }
}
