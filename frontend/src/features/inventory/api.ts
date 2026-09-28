export interface Product {
  product_id: number
  name: string
  created_at: string
  updated_at: string
}

export interface InventoryBatch {
  batch_id: number
  original_quantity: number
  remaining_quantity: number
  unit_cost: string
  currency: 'CAD'
  purchased_at: string
}

export interface InventoryItem {
  product_id: number
  product_name: string
  total_remaining_quantity: number
  batches: InventoryBatch[]
}

export interface PurchaseBatchInput {
  product_id: number
  quantity: number
  unit_cost: string
  currency: 'CAD'
  purchased_at: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...init?.headers },
  })
  let body: unknown
  try {
    body = await response.json()
  } catch {
    throw new Error('invalid_response')
  }
  if (!response.ok) throw new Error('request_failed')
  return body as T
}

export function listProducts(): Promise<Product[]> {
  return request('/api/v1/products')
}

export function createProduct(name: string): Promise<Product> {
  return request('/api/v1/products', { method: 'POST', body: JSON.stringify({ name }) })
}

export function listInventory(): Promise<InventoryItem[]> {
  return request('/api/v1/inventory')
}

export function createPurchaseBatch(input: PurchaseBatchInput): Promise<InventoryBatch> {
  return request('/api/v1/purchase-batches', { method: 'POST', body: JSON.stringify(input) })
}
