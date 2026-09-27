import { test, expect } from '@playwright/test'
import { spawn, execFileSync, type ChildProcess } from 'node:child_process'
import { once } from 'node:events'
import { createServer } from 'node:net'

function compose(...args: string[]) {
  execFileSync('docker', ['compose', '--env-file', '.env.test', '-p', 'cost-inventory-test', '-f', 'compose.test.yaml', ...args],
    { cwd: '..', stdio: 'pipe', timeout: 180000 })
}

async function stopBackend(child: ChildProcess) {
  if (child.exitCode !== null || child.signalCode !== null) return
  const exited = once(child, 'exit')
  child.kill('SIGTERM')
  await exited
}

async function startBackend() {
  // Refuse to test against or stop an unrelated service already using port 8000.
  const guard = createServer()
  guard.listen(8000, '127.0.0.1')
  await once(guard, 'listening')
  await new Promise<void>((resolve) => guard.close(() => resolve()))
  const child = spawn(process.env.BACKEND_PYTHON || '../backend/.venv/bin/python', ['../scripts/run_browser_backend.py'], { stdio: 'ignore' })
  let startError = false
  child.on('error', () => { startError = true })
  try {
    await expect.poll(async () => {
      if (startError || child.exitCode !== null) throw new Error('Test API failed to start')
      try { return (await fetch('http://127.0.0.1:8000/health/live')).status }
      catch { return 0 }
    }, { timeout: 15000 }).toBe(200)
  } catch (error) {
    if (!startError) await stopBackend(child)
    throw error
  }
  return child
}

test.describe('real stack', () => {
  test.skip(process.env.RUN_MYSQL_E2E !== '1', 'real MySQL browser test is opt-in')

  test('browser → Vite → FastAPI → MySQL; real DB and API outages', async ({ page }, testInfo) => {
  test.setTimeout(180000)
  const backend = await startBackend()
  try {
    await page.goto('/')
    await expect(page.getByRole('status')).toHaveText('所有服務正常。')
    await page.screenshot({ path: testInfo.outputPath('healthy.png') })
    try {
      compose('stop', 'db')
      await page.getByRole('button', { name: '重新檢查' }).click()
      await expect(page.getByRole('status')).toHaveText('後端正常，資料庫暫時無法使用。請稍後重試。')
      await expect(page.getByText('運作中', { exact: true })).toBeVisible()
      await expect(page.locator('code')).toHaveText(/^[a-zA-Z0-9_-]+$/)
      await page.screenshot({ path: testInfo.outputPath('database-unavailable.png') })
    } finally {
      compose('up', '-d', '--wait', '--wait-timeout', '150')
    }
    await page.getByRole('button', { name: '重新檢查' }).click()
    await expect(page.getByRole('status')).toHaveText('所有服務正常。')
    await stopBackend(backend)
    await page.getByRole('button', { name: '重新檢查' }).click()
    await expect(page.getByRole('status')).toHaveText('無法連線至後端。請確認服務已啟動後重試。')
    await page.screenshot({ path: testInfo.outputPath('backend-unavailable.png') })
  } finally {
    await stopBackend(backend)
  }
  })
})

test('loading and unavailable network are visible in the browser', async ({ page }, testInfo) => {
  let release!: () => void
  const gate = new Promise<void>((resolve) => { release = resolve })
  await page.route('**/api/health/**', async (route) => {
    await gate
    await route.abort('connectionrefused')
  })
  await page.goto('/')
  await expect(page.getByRole('status')).toHaveText('正在檢查服務狀態…')
  await page.screenshot({ path: testInfo.outputPath('loading.png') })
  release()
  await expect(page.getByRole('status')).toHaveText('無法連線至後端。請確認服務已啟動後重試。')
})
