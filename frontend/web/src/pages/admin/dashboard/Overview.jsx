import React from 'react';

const monthlyRevenue = [
  { label: 'T10', value: 210 },
  { label: 'T11', value: 242 },
  { label: 'T12', value: 275 },
  { label: 'T1', value: 260 },
  { label: 'T2', value: 318 },
  { label: 'T3', value: 342 },
  { label: 'T4', value: 331 },
  { label: 'T5', value: 376 },
  { label: 'T6', value: 411 },
  { label: 'T7', value: 390 },
  { label: 'T8', value: 448 },
  { label: 'T9', value: 482 },
];

const topProducts = [
  { name: 'Áo sơ mi linen', sales: 92 },
  { name: 'Đầm midi hoa', sales: 78 },
  { name: 'Quần jeans slim', sales: 64 },
  { name: 'Áo khoác bomber', sales: 51 },
  { name: 'Váy xếp ly', sales: 43 },
];

const chartPoints = monthlyRevenue.map((point, index) => {
  const x = 42 + (index * 520) / (monthlyRevenue.length - 1);
  const y = 188 - (point.value / 550) * 160;
  return `${x},${y}`;
}).join(' ');

const Overview = () => (
  <div className="space-y-4">
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {[
        { label: 'Doanh thu tháng', value: '482,5 tr₫', change: '▲ 12,4%', positive: true },
        { label: 'Đơn hàng', value: '1.284', change: '▲ 8,1%', positive: true },
        { label: 'Giá trị TB/đơn', value: '375 nghìn₫', change: '▼ 2,3%', positive: false },
        { label: 'Tỷ lệ thử đồ → mua', value: '18,7%', change: '▲ 3,2%', positive: true },
      ].map((stat) => (
        <div key={stat.label} className="rounded-xl border border-[#262b45] bg-[#181c30] p-4">
          <p className="text-xs font-semibold text-[#9aa2c0]">{stat.label}</p>
          <p className="mt-2 text-2xl font-bold">{stat.value}</p>
          <p className={`mt-1 text-xs font-bold ${stat.positive ? 'text-[#12a66a]' : 'text-[#e5484d]'}`}>{stat.change}</p>
        </div>
      ))}
    </div>

    <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <section className="rounded-xl border border-[#262b45] bg-[#181c30] p-4 xl:col-span-2">
        <h2 className="mb-3 text-sm font-bold">Doanh thu 12 tháng (triệu ₫)</h2>
        <div className="overflow-x-auto">
          <svg viewBox="0 0 600 230" role="img" aria-label="Biểu đồ doanh thu 12 tháng" className="h-[230px] min-w-[520px] w-full">
            {[0, 1, 2, 3, 4].map((line) => {
              const y = 188 - line * 40;
              return (
                <g key={line}>
                  <line x1="42" x2="562" y1={y} y2={y} stroke="#262b45" strokeWidth="1" />
                  <text x="4" y={y + 4} fill="#9aa2c0" fontSize="10">{line * 139}</text>
                </g>
              );
            })}
            <polygon points={`42,188 ${chartPoints} 562,188`} fill="#5b4bff" fillOpacity="0.12" />
            <polyline points={chartPoints} fill="none" stroke="#5b4bff" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
            {monthlyRevenue.map((point, index) => {
              const x = 42 + (index * 520) / (monthlyRevenue.length - 1);
              const y = 188 - (point.value / 550) * 160;
              return (
                <g key={point.label}>
                  <circle cx={x} cy={y} r="3" fill="#7568ff" />
                  <text x={x} y="214" textAnchor="middle" fill="#9aa2c0" fontSize="9">{point.label}</text>
                </g>
              );
            })}
          </svg>
        </div>
      </section>

      <section className="rounded-xl border border-[#262b45] bg-[#181c30] p-4">
        <h2 className="mb-4 text-sm font-bold">Top sản phẩm</h2>
        <div className="space-y-4">
          {topProducts.map((product) => (
            <div key={product.name}>
              <div className="mb-1.5 flex justify-between gap-2 text-xs">
                <span>{product.name}</span>
                <span className="shrink-0 font-bold text-[#9aa2c0]">{product.sales} đơn</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-[#262b45]">
                <div className="h-full rounded-full bg-[#5b4bff]" style={{ width: `${product.sales}%` }} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  </div>
);

export default Overview;