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
  const child = spawn(process.env.BACKEND_PYTHON || '../backend/.venv/bin/python', ['../scripts/run_browser_backend.py'], { stdio: 'inherit' })
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

    const productName = `商品 A ${Date.now()}`
    await page.getByLabel('商品名稱').fill(productName)
    const [createProductResponse] = await Promise.all([
      page.waitForResponse((response) =>
        response.url().endsWith('/api/v1/products') && response.request().method() === 'POST',
      { timeout: 15000 }),
      page.getByRole('button', { name: '建立商品' }).click(),
    ])
    expect(createProductResponse.status()).toBe(201)
    const createdProduct = await createProductResponse.json() as { product_id: number }
    await expect(page.getByText('商品已建立。')).toBeVisible()
    await expect(page.getByLabel('商品', { exact: true })).toHaveValue(String(createdProduct.product_id))
    await expect(page.getByLabel('試算商品')).toHaveValue(String(createdProduct.product_id))

    for (const item of [
      { quantity: '20', cost: '80', time: '2026-09-27T01:00' },
      { quantity: '10', cost: '100', time: '2026-09-28T01:00' },
    ]) {
      await page.getByLabel('進貨數量').fill(item.quantity)
      await page.getByLabel('CAD 單位成本').fill(item.cost)
      await page.getByLabel('進貨時間').fill(item.time)
      const createBatchButton = page.getByRole('button', { name: '新增進貨批次' })
      await expect(createBatchButton).toBeEnabled()
      expect(await createBatchButton.evaluate((button) => button.form?.checkValidity())).toBe(true)
      const [createBatchResponse] = await Promise.all([
        page.waitForResponse((response) =>
          response.url().endsWith('/api/v1/purchase-batches') && response.request().method() === 'POST',
        { timeout: 15000 }),
        createBatchButton.click(),
      ])
      expect(createBatchResponse.status()).toBe(201)
      await expect(page.getByText('進貨批次已新增。')).toBeVisible()
    }
    const inventoryArticle = page.locator('.inventory-list article').filter({ hasText: productName })
    await expect(inventoryArticle.getByText('總庫存 30')).toBeVisible()
    await expect(inventoryArticle.getByText('原始 20／剩餘 20')).toBeVisible()
    await expect(inventoryArticle.getByText('原始 10／剩餘 10')).toBeVisible()

    await page.getByLabel('試算數量').fill('1')
    await page.getByLabel('CAD 成交單價').fill('120')
    await page.getByRole('button', { name: '比較成本' }).click()
    const comparison = page.getByRole('region', { name: '客觀成本比較' })
    await expect(comparison.getByRole('heading', { name: 'FIFO' })).toBeVisible()
    await expect(comparison.getByText('CAD 80.00')).toBeVisible()
    await expect(comparison.getByText('CAD 86.67')).toBeVisible()
    await expect(comparison.getByText('本次試算未扣除庫存。')).toBeVisible()
    await page.screenshot({ path: testInfo.outputPath('cost-comparison-1.png'), fullPage: true })

    await page.getByLabel('試算數量').fill('25')
    await page.getByRole('button', { name: '比較成本' }).click()
    await expect(comparison.getByText('CAD 2100.00')).toBeVisible()
    await expect(comparison.getByText('CAD 2166.67')).toBeVisible()
    await page.screenshot({ path: testInfo.outputPath('cost-comparison-25.png'), fullPage: true })

    await page.getByLabel('試算數量').fill('31')
    await page.getByRole('button', { name: '比較成本' }).click()
    await expect(page.getByText('庫存不足：需要 31，目前可用 30。')).toBeVisible()

    await page.getByLabel('試算數量').fill('25')
    for (let attempt = 0; attempt < 10; attempt += 1) {
      const completed = page.waitForResponse((response) =>
        response.url().endsWith('/api/v1/simulations/cost') && response.request().method() === 'POST')
      await page.getByRole('button', { name: '比較成本' }).click()
      expect((await completed).ok()).toBe(true)
    }
    const persisted = await page.request.get('/api/v1/inventory')
    expect(persisted.ok()).toBe(true)
    const persistedInventory = await persisted.json() as Array<{
      product_name: string
      total_remaining_quantity: number
      batches: Array<{ remaining_quantity: number }>
    }>
    const demonstrated = persistedInventory.find((item) => item.product_name === productName)
    expect(demonstrated?.total_remaining_quantity).toBe(30)
    expect(demonstrated?.batches.map((item) => item.remaining_quantity)).toEqual([20, 10])
    await expect(inventoryArticle.getByText('總庫存 30')).toBeVisible()
    await page.screenshot({ path: testInfo.outputPath('inventory-unchanged.png'), fullPage: true })

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
