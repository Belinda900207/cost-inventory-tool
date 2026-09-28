import type { ComparedMethod, CostMethodResult, CostSimulation } from './api'

function methodName(method: ComparedMethod) {
  if (method === 'fifo') return 'FIFO'
  if (method === 'weighted_average') return '數量加權平均'
  return '兩者相同'
}

function differenceText(
  label: string,
  difference: { amount: string; higher_method: ComparedMethod },
) {
  const direction = difference.higher_method === 'equal'
    ? '兩者相同。'
    : `${methodName(difference.higher_method)}${difference.higher_method === 'fifo' ? ' ' : ''}較高。`
  return `${label}差額 CAD ${difference.amount}；${direction}`
}

function MethodCard({ title, result, revenue }: {
  title: string
  result: CostMethodResult
  revenue: string
}) {
  return (
    <article className="method-card">
      <h4>{title}</h4>
      <dl>
        <div><dt>單位成本</dt><dd>CAD {result.unit_cost}</dd></div>
        <div><dt>總成本</dt><dd>CAD {result.total_cost}</dd></div>
        <div><dt>試算營收</dt><dd>CAD {revenue}</dd></div>
        <div><dt>試算毛利</dt><dd>CAD {result.gross_profit}</dd></div>
        <div><dt>試算毛利率</dt><dd>{result.gross_margin_percent}%</dd></div>
      </dl>
    </article>
  )
}

export default function CostComparison({ result }: { result: CostSimulation }) {
  return (
    <section className="cost-results" aria-labelledby="cost-results-title">
      <header>
        <h3 id="cost-results-title">客觀成本比較</h3>
        <p>{result.quantity} 個 × CAD {result.selling_unit_price}</p>
      </header>
      <p>兩種方法地位相同，請依你的使用情境自行比較。</p>
      <div className="method-grid">
        <MethodCard title="FIFO" result={result.fifo} revenue={result.revenue} />
        <MethodCard
          title="數量加權平均"
          result={result.weighted_average}
          revenue={result.revenue}
        />
      </div>
      <div className="difference-summary" aria-label="客觀差額">
        <p>{differenceText('總成本', result.difference.total_cost)}</p>
        <p>{differenceText('試算毛利', result.difference.gross_profit)}</p>
      </div>
      <p className="disclaimer">{result.disclaimer}</p>
      {!result.inventory_changed && <p className="inventory-unchanged">本次試算未扣除庫存。</p>}
    </section>
  )
}
