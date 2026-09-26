import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import App from './App'

function reply(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'X-Request-ID': 'test-trace' } })
}
function healthyFetch() {
  return vi.fn().mockImplementation((url: string) => Promise.resolve(
    reply(url.endsWith('/live') ? { status: 'ok' } : { status: 'ok', database: 'ok' }),
  ))
}
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

describe('服務狀態頁', () => {
  it('顯示載入中並禁止重複請求', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<App />)
    expect(screen.getByRole('status').textContent).toContain('正在檢查')
    expect((screen.getByRole('button') as HTMLButtonElement).disabled).toBe(true)
  })
  it('透過相對 API URL 顯示成功', async () => {
    const fetchMock = healthyFetch()
    vi.stubGlobal('fetch', fetchMock)
    render(<App />)
    await screen.findByText('所有服務正常。')
    expect(screen.getByText('連線正常')).toBeTruthy()
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual(['/api/health/live', '/api/health/ready'])
  })
  it('DB 503 顯示資料庫故障與追蹤編號，重試可恢復', async () => {
    const fetchMock = vi.fn().mockImplementation((url: string) => Promise.resolve(url.endsWith('/live')
      ? reply({ status: 'ok' })
      : reply({ error: { code: 'database_unavailable' } }, 503)))
    vi.stubGlobal('fetch', fetchMock)
    render(<App />)
    await screen.findByText('後端正常，資料庫暫時無法使用。請稍後重試。')
    expect(screen.getByText('test-trace')).toBeTruthy()
    vi.stubGlobal('fetch', healthyFetch())
    fireEvent.click(screen.getByRole('button'))
    await screen.findByText('所有服務正常。')
  })
  it('網路失敗顯示後端斷線，不冒稱 DB 故障', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('private network detail')))
    render(<App />)
    await screen.findByText('無法連線至後端。請確認服務已啟動後重試。')
    expect(screen.getByText('無法確認')).toBeTruthy()
    expect(screen.queryByText(/private network/)).toBeNull()
  })
  it('ready 非 JSON 回應顯示未知狀態', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => Promise.resolve(url.endsWith('/live')
      ? reply({ status: 'ok' }) : new Response('proxy error', { status: 502 }))))
    render(<App />)
    await screen.findByText('後端可連線，但無法確認資料庫狀態。請稍後重試。')
  })
  it('拒絕不符合合約的成功 body', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(reply({ status: 'ok' }))))
    render(<App />)
    await screen.findByText('後端可連線，但無法確認資料庫狀態。請稍後重試。')
  })
  it('卸載時取消尚未完成的請求', () => {
    const fetchMock = vi.fn(() => new Promise(() => {}))
    vi.stubGlobal('fetch', fetchMock)
    const { unmount } = render(<App />)
    const signal = (fetchMock.mock.calls as unknown as [string, RequestInit][])[0][1].signal
    unmount()
    expect(signal?.aborted).toBe(true)
  })
})
