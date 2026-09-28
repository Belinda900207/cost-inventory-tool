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

export type CostMethod = 'fifo' | 'weighted_average'
export type ComparedMethod = CostMethod | 'equal'

export interface CostMethodResult {
  method: CostMethod
  unit_cost: string
  total_cost: string
  gross_profit: string
  gross_margin_percent: string
}

export interface CostSimulation {
  product_id: number
  quantity: number
  currency: 'CAD'
  selling_unit_price: string
  revenue: string
  fifo: CostMethodResult
  weighted_average: CostMethodResult
  difference: {
    total_cost: { amount: string; higher_method: ComparedMethod }
    gross_profit: { amount: string; higher_method: ComparedMethod }
  }
  inventory_changed: false
  disclaimer: string
}

export interface CostSimulationInput {
  product_id: number
  quantity: number
  selling_unit_price: string
  currency: 'CAD'
}

export class ApiRequestError extends Error {
  readonly status: number
  readonly code: string
  readonly details: Record<string, string | number>

  constructor(
    status: number,
    code: string,
    details: Record<string, string | number> = {},
  ) {
    super(code)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
    this.details = details
  }
}

function errorDetails(body: unknown): { code: string; details: Record<string, string | number> } {
  if (!body || typeof body !== 'object' || !('error' in body)) {
    return { code: 'request_failed', details: {} }
  }
  const error = body.error
  if (!error || typeof error !== 'object') return { code: 'request_failed', details: {} }
  const code = 'code' in error && typeof error.code === 'string' ? error.code : 'request_failed'
  const details = 'details' in error && error.details && typeof error.details === 'object'
    ? Object.fromEntries(Object.entries(error.details).filter(([, value]) =>
      typeof value === 'string' || typeof value === 'number'))
    : {}
  return { code, details }
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
  if (!response.ok) {
    const error = errorDetails(body)
    throw new ApiRequestError(response.status, error.code, error.details)
  }
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

export function simulateCost(input: CostSimulationInput): Promise<CostSimulation> {
  return request('/api/v1/simulations/cost', { method: 'POST', body: JSON.stringify(input) })
}
