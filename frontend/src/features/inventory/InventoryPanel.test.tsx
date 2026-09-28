import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import InventoryPanel from './InventoryPanel'
import * as inventoryApi from './api'

vi.mock('./api')

const product = {
  product_id: 1,
  name: 'Product A',
  created_at: '2026-09-28T04:00:00Z',
  updated_at: '2026-09-28T04:00:00Z',
}
const inventory = {
  product_id: 1,
  product_name: 'Product A',
  total_remaining_quantity: 30,
  batches: [
    {
      batch_id: 1,
      original_quantity: 20,
      remaining_quantity: 20,
      unit_cost: '80.00',
      currency: 'CAD' as const,
      purchased_at: '2026-09-27T01:00:00Z',
    },
    {
      batch_id: 2,
      original_quantity: 10,
      remaining_quantity: 10,
      unit_cost: '100.00',
      currency: 'CAD' as const,
      purchased_at: '2026-09-28T01:00:00Z',
    },
  ],
}
const simulation: inventoryApi.CostSimulation = {
  product_id: 1,
  quantity: 25,
  currency: 'CAD',
  selling_unit_price: '120.00',
  revenue: '3000.00',
  fifo: {
    method: 'fifo',
    unit_cost: '84.00',
    total_cost: '2100.00',
    gross_profit: '900.00',
    gross_margin_percent: '30.00',
  },
  weighted_average: {
    method: 'weighted_average',
    unit_cost: '86.67',
    total_cost: '2166.67',
    gross_profit: '833.33',
    gross_margin_percent: '27.78',
  },
  difference: {
    total_cost: { amount: '66.67', higher_method: 'weighted_average' },
    gross_profit: { amount: '66.67', higher_method: 'fifo' },
  },
  inventory_changed: false,
  disclaimer: '此結果僅供成本比較，不是正式會計淨利。',
}

afterEach(() => {
  cleanup()
  vi.resetAllMocks()
})

describe('商品、進貨與庫存', () => {
  it('顯示 MySQL API 回傳的總庫存與批次', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([inventory])
    render(<InventoryPanel />)

    await screen.findByText('總庫存 30')
    expect(screen.getByText('CAD 80.00')).toBeTruthy()
    expect(screen.getByText('CAD 100.00')).toBeTruthy()
    expect(screen.getByText('原始 20／剩餘 20')).toBeTruthy()
  })

  it('可建立商品並重新載入庫存', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([])
    vi.mocked(inventoryApi.createProduct).mockResolvedValue(product)
    render(<InventoryPanel />)

    fireEvent.change(screen.getByLabelText('商品名稱'), { target: { value: ' Product A ' } })
    fireEvent.click(screen.getByRole('button', { name: '建立商品' }))

    await waitFor(() => expect(inventoryApi.createProduct).toHaveBeenCalledWith(' Product A '))
    expect(await screen.findByText('商品已建立。')).toBeTruthy()
  })

  it('可輸入一批進貨並使用 CAD', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([])
    vi.mocked(inventoryApi.createPurchaseBatch).mockResolvedValue(inventory.batches[0])
    render(<InventoryPanel />)

    await waitFor(() => expect(
      (screen.getByLabelText('試算商品') as HTMLSelectElement).value,
    ).toBe('1'))
    fireEvent.change(screen.getByLabelText('進貨數量'), { target: { value: '20' } })
    fireEvent.change(screen.getByLabelText('CAD 單位成本'), { target: { value: '80.00' } })
    fireEvent.change(screen.getByLabelText('進貨時間'), { target: { value: '2026-09-27T01:00' } })
    fireEvent.click(screen.getByRole('button', { name: '新增進貨批次' }))

    const expectedTime = new Date('2026-09-27T01:00').toISOString()
    await waitFor(() => expect(inventoryApi.createPurchaseBatch).toHaveBeenCalledWith({
      product_id: 1,
      quantity: 20,
      unit_cost: '80.00',
      currency: 'CAD',
      purchased_at: expectedTime,
    }))
  })

  it('將 FIFO 與加權平均並排呈現且不推薦算法', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([inventory])
    vi.mocked(inventoryApi.simulateCost).mockResolvedValue(simulation)
    render(<InventoryPanel />)

    await waitFor(() => expect(
      (screen.getByLabelText('試算商品') as HTMLSelectElement).value,
    ).toBe('1'))
    fireEvent.change(screen.getByLabelText('試算數量'), { target: { value: '25' } })
    fireEvent.change(screen.getByLabelText('CAD 成交單價'), { target: { value: '120.00' } })
    fireEvent.click(screen.getByRole('button', { name: '比較成本' }))

    expect(await screen.findByRole('heading', { name: 'FIFO' })).toBeTruthy()
    expect(screen.getByRole('heading', { name: '數量加權平均' })).toBeTruthy()
    expect(screen.getByText('CAD 2100.00')).toBeTruthy()
    expect(screen.getByText('CAD 2166.67')).toBeTruthy()
    expect(screen.getByText('總成本差額 CAD 66.67；數量加權平均較高。')).toBeTruthy()
    expect(screen.getByText('試算毛利差額 CAD 66.67；FIFO 較高。')).toBeTruthy()
    expect(screen.getByText('此結果僅供成本比較，不是正式會計淨利。')).toBeTruthy()
    expect(screen.getByText('本次試算未扣除庫存。')).toBeTruthy()
    expect(screen.queryByText(/推薦/)).toBeNull()
    expect(inventoryApi.listInventory).toHaveBeenCalledTimes(1)
  })

  it('顯示 client validation 且不呼叫 API', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([inventory])
    render(<InventoryPanel />)
    const heading = await screen.findByRole('heading', { name: '成本試算' })

    fireEvent.submit(heading.closest('form')!)

    expect(await screen.findByText('請輸入正整數數量與大於零的 CAD 成交單價。')).toBeTruthy()
    expect(inventoryApi.simulateCost).not.toHaveBeenCalled()
  })

  it('試算期間顯示 loading 並禁止重複送出', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([inventory])
    vi.mocked(inventoryApi.simulateCost).mockReturnValue(new Promise(() => {}))
    render(<InventoryPanel />)

    await waitFor(() => expect(
      (screen.getByLabelText('試算商品') as HTMLSelectElement).value,
    ).toBe('1'))
    fireEvent.change(screen.getByLabelText('試算數量'), { target: { value: '25' } })
    fireEvent.change(screen.getByLabelText('CAD 成交單價'), { target: { value: '120' } })
    fireEvent.click(screen.getByRole('button', { name: '比較成本' }))

    const button = await screen.findByRole('button', { name: '試算中…' })
    expect((button as HTMLButtonElement).disabled).toBe(true)
  })

  it('分別顯示庫存不足與一般後端失敗', async () => {
    vi.mocked(inventoryApi.listProducts).mockResolvedValue([product])
    vi.mocked(inventoryApi.listInventory).mockResolvedValue([inventory])
    vi.mocked(inventoryApi.simulateCost)
      .mockRejectedValueOnce({
        status: 409,
        code: 'insufficient_inventory',
        details: { requested: 31, available: 30 },
      })
      .mockRejectedValueOnce(new Error('network detail'))
    render(<InventoryPanel />)

    await waitFor(() => expect(
      (screen.getByLabelText('試算商品') as HTMLSelectElement).value,
    ).toBe('1'))
    fireEvent.change(screen.getByLabelText('試算數量'), { target: { value: '31' } })
    fireEvent.change(screen.getByLabelText('CAD 成交單價'), { target: { value: '120' } })
    fireEvent.click(screen.getByRole('button', { name: '比較成本' }))
    expect(await screen.findByText('庫存不足：需要 31，目前可用 30。')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('試算數量'), { target: { value: '25' } })
    fireEvent.click(screen.getByRole('button', { name: '比較成本' }))
    expect(await screen.findByText('試算失敗；請確認後端與資料庫狀態後重試。')).toBeTruthy()
    expect(screen.queryByText(/network detail/)).toBeNull()
  })
})
