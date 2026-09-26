import { useEffect, useState } from 'react'
import { getHealth } from './api/client'
import type { HealthState } from './api/client'
import './App.css'

export default function App() {
  const [state, setState] = useState<HealthState>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    void getHealth(controller.signal).then((result) => {
      if (!controller.signal.aborted) setState(result)
    })
    return () => controller.abort()
  }, [attempt])

  const backend = state.kind === 'loading' ? '檢查中' :
    state.kind === 'backend-unavailable' ? '無法連線' : '運作中'
  const database = state.kind === 'loading' ? '檢查中' :
    state.kind === 'healthy' ? '連線正常' :
    state.kind === 'database-unavailable' ? '暫時無法使用' : '無法確認'
  const message = state.kind === 'loading' ? '正在檢查服務狀態…' :
    state.kind === 'healthy' ? '所有服務正常。' :
    state.kind === 'database-unavailable' ? '後端正常，資料庫暫時無法使用。請稍後重試。' :
    state.kind === 'backend-unavailable' ? '無法連線至後端。請確認服務已啟動後重試。' :
    '後端可連線，但無法確認資料庫狀態。請稍後重試。'

  return (
    <main>
      <h1>成本與庫存工具</h1>
      <p>服務狀態</p>
      <section aria-label="服務健康狀態" aria-live="polite" aria-busy={state.kind === 'loading'}>
        <p role="status">{message}</p>
        <dl>
          <div><dt>FastAPI 後端</dt><dd>{backend}</dd></div>
          <div><dt>MySQL 資料庫</dt><dd>{database}</dd></div>
        </dl>
        {'requestId' in state && state.requestId && <p>追蹤編號：<code>{state.requestId}</code></p>}
      </section>
      <button disabled={state.kind === 'loading'} onClick={() => {
        setState({ kind: 'loading' })
        setAttempt((value) => value + 1)
      }}>重新檢查</button>
    </main>
  )
}
