import React, { useCallback, useEffect, useMemo, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const inputClass = 'rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2 text-sm text-white outline-none focus:border-[#0f9d8a]';

const getStockState = (quantity) => quantity <= 0 ? 'out' : quantity <= 5 ? 'low' : 'available';
const stateLabels = { available: 'Còn hàng', low: 'Sắp hết', out: 'Hết hàng' };
const stateStyles = {
  available: 'bg-[#0f2e24] text-[#12a66a]',
  low: 'bg-[#3a2e12] text-[#e8930c]',
  out: 'bg-[#3a1a1e] text-[#e5484d]',
};

const StockAdjustments = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [stateFilter, setStateFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [adjustment, setAdjustment] = useState({ mode: 'add', quantity: '1', reason: '' });

  const loadItems = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const result = await apiClient.get('inventory/variants?page=1&limit=100');
      setItems(result.items || []);
    } catch (loadError) { setError(loadError.message); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { loadItems(); }, [loadItems]);

  const submitAdjustment = async (event) => {
    event.preventDefault(); if (!selected) return;
    const quantity = Number(adjustment.quantity);
    const delta = adjustment.mode === 'set' ? quantity - selected.stock_on_hand : adjustment.mode === 'subtract' ? -quantity : quantity;
    if (!delta) { setError('Số lượng mới bằng tồn hiện tại, không cần điều chỉnh.'); return; }
    setError('');
    try {
      await apiClient.post(`inventory/variants/${selected.variant_id}/adjustments`, { delta, reason: adjustment.reason.trim() });
      setSelected(null);
      await loadItems();
    } catch (submitError) { setError(submitError.message); }
  };

  const totals = useMemo(() => items.reduce((result, item) => {
    const state = getStockState(item.stock_on_hand);
    result.quantity += item.stock_on_hand;
    result.variants += 1;
    result[state] += 1;
    return result;
  }, { quantity: 0, variants: 0, available: 0, low: 0, out: 0 }), [items]);

  const filteredItems = items.filter((item) => {
    const matchesQuery = !query || `${item.product_name} ${item.sku} ${item.color} ${item.size}`.toLowerCase().includes(query.toLowerCase());
    return matchesQuery && (stateFilter === 'all' || getStockState(item.stock_on_hand) === stateFilter);
  });

  const summary = [
    ['Tổng tồn', totals.quantity],
    ['Biến thể', totals.variants],
    ['Sắp hết (≤5)', totals.low],
    ['Hết hàng', totals.out],
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Danh sách tồn kho</h1>
        <select className={inputClass} value={stateFilter} onChange={(event) => setStateFilter(event.target.value)} aria-label="Lọc trạng thái tồn kho">
          <option value="all">Tất cả</option>
          <option value="available">Còn hàng</option>
          <option value="low">Sắp hết (≤5)</option>
          <option value="out">Hết hàng</option>
        </select>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {summary.map(([label, value]) => <article key={label} className="rounded-xl border border-[#24383b] bg-[#152427] p-4"><p className="text-xs text-[#92a9ad]">{label}</p><p className="mt-1 text-2xl font-bold">{value}</p></article>)}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <input className={`${inputClass} min-w-64`} placeholder="Tìm sản phẩm / SKU / màu / size" value={query} onChange={(event) => setQuery(event.target.value)} />
        <button className="text-sm text-[#0f9d8a]" onClick={loadItems}>Tải lại</button>
      </div>
      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}

      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Sản phẩm</th><th className="p-3">Màu</th><th className="p-3">Size</th><th className="p-3">Tồn</th><th className="p-3">Trạng thái</th><th className="p-3" /></tr></thead>
          <tbody>
            {!loading && filteredItems.map((item) => {
              const state = getStockState(item.stock_on_hand);
              return <tr key={item.variant_id} className="border-b border-[#24383b] last:border-0"><td className="p-3 font-semibold">{item.product_name}<span className="ml-2 text-xs font-normal text-[#92a9ad]">{item.sku}</span></td><td className="p-3">{item.color || '—'}</td><td className="p-3">{item.size}</td><td className="p-3 font-bold">{item.stock_on_hand}</td><td className="p-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${stateStyles[state]}`}>{stateLabels[state]}{state === 'low' ? ' (≤5)' : ''}</span></td><td className="p-3"><button className="rounded-lg border border-[#24383b] px-3 py-1 text-xs hover:border-[#0f9d8a]" onClick={() => { setSelected(item); setAdjustment({ mode: 'add', quantity: '1', reason: '' }); }}>Điều chỉnh</button></td></tr>;
            })}
            {!loading && filteredItems.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">{items.length ? 'Không có biến thể khớp bộ lọc.' : 'Chưa có biến thể tồn kho.'}</td></tr>}
            {loading && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Đang tải dữ liệu…</td></tr>}
          </tbody>
        </table>
      </div>

      {selected && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"><form onSubmit={submitAdjustment} className="w-full max-w-md space-y-3 rounded-xl border border-[#24383b] bg-[#152427] p-5"><h2 className="font-bold">Điều chỉnh tồn kho</h2><p className="text-sm text-[#92a9ad]">{selected.product_name} · {selected.color} / {selected.size} · hiện có {selected.stock_on_hand}</p><select className={`${inputClass} w-full`} value={adjustment.mode} onChange={(event) => setAdjustment({ ...adjustment, mode: event.target.value })}><option value="add">Nhập thêm</option><option value="subtract">Xuất bớt</option><option value="set">Đặt tồn thực tế</option></select><input className={`${inputClass} w-full`} type="number" min="1" value={adjustment.quantity} onChange={(event) => setAdjustment({ ...adjustment, quantity: event.target.value })} required /><textarea className={`${inputClass} w-full`} rows="3" placeholder="Lý do điều chỉnh (bắt buộc)" value={adjustment.reason} onChange={(event) => setAdjustment({ ...adjustment, reason: event.target.value })} required minLength="3" /><div className="flex justify-end gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2" onClick={() => setSelected(null)}>Hủy</button><button className="rounded-lg bg-[#0f9d8a] px-4 py-2 font-bold">Xác nhận</button></div></form></div>}
    </div>
  );
};

export default StockAdjustments;
