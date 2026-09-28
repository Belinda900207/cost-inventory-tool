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

    await screen.findByRole('option', { name: 'Product A' })
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
})
