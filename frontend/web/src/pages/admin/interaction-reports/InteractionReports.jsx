import React from 'react';

const products = [
  { name: 'Áo sơ mi linen', qr: 1420, views: 3260, tryOn: 890, conversion: 63 },
  { name: 'Đầm midi hoa', qr: 1180, views: 2940, tryOn: 1010, conversion: 86 },
  { name: 'Quần jeans slim', qr: 960, views: 2410, tryOn: 640, conversion: 67 },
  { name: 'Áo khoác bomber', qr: 720, views: 1880, tryOn: 560, conversion: 78 },
  { name: 'Váy xếp ly', qr: 640, views: 1520, tryOn: 470, conversion: 73 },
];

const trend = [352, 430, 398, 482, 561, 534, 602, 648, 619, 688, 664, 731, 780, 842];

const InteractionReports = () => {
  const exportCsv = () => {
    const rows = [['Sản phẩm', 'Quét QR', 'Lượt xem', 'Thử đồ', 'Chuyển đổi'], ...products.map((product) => [product.name, product.qr, product.views, product.tryOn, `${product.conversion}%`])];
    const csv = `\uFEFF${rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\r\n')}`;
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'thong-ke-tuong-tac.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  const points = trend.map((value, index) => `${44 + (index * 570) / (trend.length - 1)},${170 - (value / 900) * 145}`).join(' ');

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Thống kê quét QR, lượt xem &amp; thử đồ</h1>
        <button type="button" onClick={exportCsv} className="shrink-0 rounded-lg bg-[#5b4bff] px-4 py-2 text-xs font-bold text-white hover:bg-[#4a3ecc]">⇩ Xuất báo cáo</button>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {[
          { label: 'Lượt quét QR', value: '8.420', change: '▲ 14%' },
          { label: 'Lượt xem sản phẩm', value: '21.960', change: '▲ 9%' },
          { label: 'Lượt thử đồ AI', value: '5.318', change: '▲ 22%' },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-[#262b45] bg-[#181c30] p-4">
            <p className="text-xs font-semibold text-[#9aa2c0]">{stat.label}</p>
            <p className="mt-1 text-2xl font-bold">{stat.value}</p>
            <p className="mt-1 text-xs font-bold text-[#12a66a]">{stat.change}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="rounded-xl border border-[#262b45] bg-[#181c30] p-4 xl:col-span-2">
          <h2 className="mb-3 text-sm font-bold">Lượt quét QR 14 ngày</h2>
          <div className="overflow-x-auto">
            <svg viewBox="0 0 640 210" role="img" aria-label="Biểu đồ lượt quét QR 14 ngày" className="h-[210px] min-w-[540px] w-full">
              {[0, 1, 2, 3, 4].map((line) => {
                const y = 170 - line * 36;
                return <g key={line}><line x1="44" x2="614" y1={y} y2={y} stroke="#262b45" /><text x="4" y={y + 4} fill="#9aa2c0" fontSize="10">{line * 218}</text></g>;
              })}
              <polygon points={`44,170 ${points} 614,170`} fill="#5b4bff" fillOpacity="0.12" />
              <polyline points={points} fill="none" stroke="#5b4bff" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
              {trend.map((value, index) => {
                const x = 44 + (index * 570) / (trend.length - 1);
                const y = 170 - (value / 900) * 145;
                return <circle key={`${value}-${index}`} cx={x} cy={y} r="3" fill="#7568ff" />;
              })}
              {[1, 4, 7, 10, 13].map((day) => <text key={day} x={44 + (day * 570) / (trend.length - 1)} y="198" textAnchor="middle" fill="#9aa2c0" fontSize="10">{day + 1}</text>)}
            </svg>
          </div>
        </section>

        <section className="rounded-xl border border-[#262b45] bg-[#181c30] p-4">
          <h2 className="mb-4 text-sm font-bold">Phễu chuyển đổi</h2>
          <div className="space-y-4">
            {[
              { label: 'Quét QR', value: 8420 },
              { label: 'Xem sản phẩm', value: 6150 },
              { label: 'Thử đồ', value: 5318 },
              { label: 'Thêm giỏ', value: 2104 },
              { label: 'Đặt hàng', value: 994 },
            ].map((step) => (
              <div key={step.label}>
                <div className="mb-1 flex justify-between text-xs"><span>{step.label}</span><span className="font-bold">{new Intl.NumberFormat('vi-VN').format(step.value)}</span></div>
                <div className="h-1.5 overflow-hidden rounded-full bg-[#262b45]"><div className="h-full rounded-full bg-[#5b4bff]" style={{ width: `${(step.value / 8420) * 100}%` }} /></div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[#262b45] bg-[#181c30]">
        <table className="w-full min-w-[700px] text-left">
          <thead><tr className="border-b border-[#262b45] text-xs text-[#9aa2c0]">{['Sản phẩm', 'Quét QR', 'Lượt xem', 'Thử đồ', 'Chuyển đổi'].map((heading) => <th key={heading} className="px-4 py-3 font-semibold">{heading}</th>)}</tr></thead>
          <tbody className="text-xs">
            {products.map((product) => (
              <tr key={product.name} className="border-b border-[#262b45] last:border-0 hover:bg-[#20243a]">
                <td className="px-4 py-3">{product.name}</td>
                <td className="px-4 py-3">{new Intl.NumberFormat('vi-VN').format(product.qr)}</td>
                <td className="px-4 py-3">{new Intl.NumberFormat('vi-VN').format(product.views)}</td>
                <td className="px-4 py-3">{new Intl.NumberFormat('vi-VN').format(product.tryOn)}</td>
                <td className="px-4 py-3"><span className="rounded-full bg-[#0f2e24] px-2.5 py-1 font-bold text-[#12a66a]">{product.conversion}%</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InteractionReports;