import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const StockHistory = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiClient.get('inventory/adjustments?page=1&limit=100');
      setItems(result.items || []);
    } catch (loadError) { setError(loadError.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3"><h1 className="text-lg font-bold">Lịch sử điều chỉnh tồn</h1><button className="text-sm text-[#0f9d8a]" onClick={loadHistory}>Tải lại</button></div>
      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}
      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Thời gian</th><th className="p-3">Sản phẩm</th><th className="p-3">Biến thể</th><th className="p-3">Loại</th><th className="p-3">Số lượng</th><th className="p-3">Lý do</th><th className="p-3">Người thực hiện</th></tr></thead>
          <tbody>
            {!loading && items.map((item) => <tr key={item.id} className="border-b border-[#24383b] last:border-0"><td className="whitespace-nowrap p-3">{new Date(item.created_at).toLocaleString()}</td><td className="p-3 font-semibold">{item.product_name}</td><td className="p-3">{item.color || '—'} / {item.size} · {item.sku}</td><td className="p-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${item.delta > 0 ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a2e12] text-[#e8930c]'}`}>{item.delta > 0 ? 'Nhập' : 'Xuất'}</span></td><td className="p-3 font-semibold">{item.delta > 0 ? '+' : ''}{item.delta}<span className="ml-2 text-xs font-normal text-[#92a9ad]">{item.quantity_before} → {item.quantity_after}</span></td><td className="p-3">{item.reason}</td><td className="p-3">{item.changed_by_name || item.changed_by_account || '—'}</td></tr>)}
            {!loading && items.length === 0 && <tr><td colSpan="7" className="p-8 text-center text-[#92a9ad]">Chưa có lịch sử điều chỉnh tồn.</td></tr>}
            {loading && <tr><td colSpan="7" className="p-8 text-center text-[#92a9ad]">Đang tải dữ liệu…</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StockHistory;
