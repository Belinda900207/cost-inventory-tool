import { type FormEvent, useCallback, useEffect, useState } from 'react'
import {
  createProduct,
  createPurchaseBatch,
  listInventory,
  listProducts,
  type InventoryItem,
  type Product,
} from './api'
import './inventory.css'

export default function InventoryPanel() {
  const [products, setProducts] = useState<Product[]>([])
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [productName, setProductName] = useState('')
  const [selectedProduct, setSelectedProduct] = useState('')
  const [quantity, setQuantity] = useState('')
  const [unitCost, setUnitCost] = useState('')
  const [purchasedAt, setPurchasedAt] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [failed, setFailed] = useState(false)

  const load = useCallback(async () => {
    try {
      const [nextProducts, nextInventory] = await Promise.all([listProducts(), listInventory()])
      setProducts(nextProducts)
      setInventory(nextInventory)
      setSelectedProduct((current) => current || String(nextProducts[0]?.product_id ?? ''))
      setFailed(false)
    } catch {
      setFailed(true)
    }
  }, [])

  useEffect(() => {
    let active = true
    void Promise.all([listProducts(), listInventory()]).then(([nextProducts, nextInventory]) => {
      if (!active) return
      setProducts(nextProducts)
      setInventory(nextInventory)
      setSelectedProduct(String(nextProducts[0]?.product_id ?? ''))
      setFailed(false)
    }).catch(() => {
      if (active) setFailed(true)
    })
    return () => { active = false }
  }, [])

  async function submitProduct(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    try {
      await createProduct(productName)
      setProductName('')
      setMessage('商品已建立。')
      await load()
    } catch {
      setMessage('商品建立失敗；名稱可能已存在或格式不正確。')
    } finally {
      setBusy(false)
    }
  }

  async function submitBatch(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    try {
      await createPurchaseBatch({
        product_id: Number(selectedProduct),
        quantity: Number(quantity),
        unit_cost: unitCost,
        currency: 'CAD',
        purchased_at: new Date(purchasedAt).toISOString(),
      })
      setQuantity('')
      setUnitCost('')
      setPurchasedAt('')
      setMessage('進貨批次已新增。')
      await load()
    } catch {
      setMessage('進貨建立失敗；請確認商品、正整數數量、CAD 成本與時間。')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="inventory-panel" aria-labelledby="inventory-title">
      <h2 id="inventory-title">商品與庫存</h2>
      <p>建立商品與 CAD 進貨批次。此 MVP 尚未提供正式扣庫存功能。</p>
      {failed && <p role="alert">無法載入商品與庫存，請確認後端與資料庫狀態。</p>}
      {message && <p aria-live="polite">{message}</p>}

      <div className="inventory-forms">
        <form onSubmit={(event) => void submitProduct(event)}>
          <h3>建立商品</h3>
          <label>商品名稱<input required value={productName} onChange={(event) => setProductName(event.target.value)} /></label>
          <button disabled={busy}>建立商品</button>
        </form>

        <form onSubmit={(event) => void submitBatch(event)}>
          <h3>新增進貨批次</h3>
          <label>商品<select required value={selectedProduct} onChange={(event) => setSelectedProduct(event.target.value)}>
            <option value="">請選擇</option>
            {products.map((product) => <option key={product.product_id} value={product.product_id}>{product.name}</option>)}
          </select></label>
          <label>進貨數量<input required min="1" step="1" type="number" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></label>
          <label>CAD 單位成本<input required min="0.000001" step="0.000001" inputMode="decimal" type="number" value={unitCost} onChange={(event) => setUnitCost(event.target.value)} /></label>
          <label>進貨時間<input required type="datetime-local" value={purchasedAt} onChange={(event) => setPurchasedAt(event.target.value)} /></label>
          <button disabled={busy || products.length === 0}>新增進貨批次</button>
        </form>
      </div>

      <div className="inventory-list">
        {inventory.length === 0 && !failed && <p>尚無庫存資料。</p>}
        {inventory.map((item) => (
          <article key={item.product_id}>
            <header><h3>{item.product_name}</h3><strong>總庫存 {item.total_remaining_quantity}</strong></header>
            {item.batches.length === 0 ? <p>尚無進貨批次。</p> : <ul>
              {item.batches.map((batch) => <li key={batch.batch_id}>
                <span>CAD {batch.unit_cost}</span>
                <span>原始 {batch.original_quantity}／剩餘 {batch.remaining_quantity}</span>
                <time dateTime={batch.purchased_at}>{new Date(batch.purchased_at).toLocaleString()}</time>
              </li>)}
            </ul>}
          </article>
        ))}
      </div>
    </section>
  )
}
