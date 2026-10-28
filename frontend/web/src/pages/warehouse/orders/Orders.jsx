import React, { useCallback, useEffect, useMemo, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const statusLabels = {
  confirmed: 'Chờ chuẩn bị',
  processing: 'Đang đóng gói',
  ready_to_ship: 'Đang đóng gói',
  shipped: 'Đã bàn giao vận chuyển',
  completed: 'Đã bàn giao vận chuyển',
  pending_confirmation: 'Chờ xác nhận',
  cancelled: 'Đã hủy',
  expired: 'Hết hạn',
};
const statusStyles = {
  confirmed: 'bg-amber-500/10 text-amber-300',
  processing: 'bg-blue-500/10 text-blue-300',
  ready_to_ship: 'bg-blue-500/10 text-blue-300',
  shipped: 'bg-emerald-500/10 text-emerald-300',
  completed: 'bg-emerald-500/10 text-emerald-300',
};
const paymentMethods = { cod: 'COD', vnpay: 'VNPay', cash: 'Tiền mặt', card: 'Thẻ', bank_transfer: 'Chuyển khoản' };
const paymentStatuses = { paid: 'Đã thanh toán', unpaid: 'Chưa thanh toán', refunded: 'Đã hoàn tiền' };
const filters = [
  { id: 'all', label: 'Tất cả' },
  { id: 'confirmed', label: 'Chờ chuẩn bị' },
  { id: 'packing', label: 'Đang đóng gói' },
  { id: 'shipped', label: 'Đã bàn giao' },
];
const trackedStatuses = ['confirmed', 'processing', 'ready_to_ship', 'shipped', 'completed'];
const progressFor = (status) => status === 'confirmed' ? 0 : ['processing', 'ready_to_ship'].includes(status) ? 1 : 2;
const formatOrderNumber = (number) => number?.startsWith('#') ? number : `#${number || ''}`;

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState('all');
  const [detail, setDetail] = useState(null);
  const [checkedItems, setCheckedItems] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');

  const loadOrders = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiClient.get('orders?page=1&limit=100');
      setOrders((result.items || []).filter((order) => trackedStatuses.includes(order.status)));
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  const counts = useMemo(() => ({
    confirmed: orders.filter((order) => order.status === 'confirmed').length,
    packing: orders.filter((order) => ['processing', 'ready_to_ship'].includes(order.status)).length,
    shipped: orders.filter((order) => ['shipped', 'completed'].includes(order.status)).length,
    all: orders.length,
  }), [orders]);

  const visibleOrders = useMemo(() => orders.filter((order) => {
    if (filter === 'all') return true;
    if (filter === 'packing') return ['processing', 'ready_to_ship'].includes(order.status);
    if (filter === 'shipped') return ['shipped', 'completed'].includes(order.status);
    return order.status === filter;
  }), [orders, filter]);

  const openDetail = async (order) => {
    setDetailLoading(true);
    setError('');
    setCheckedItems(new Set());
    try {
      setDetail(await apiClient.get(`orders/${order.id}`));
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setDetailLoading(false);
    }
  };

  const toggleItem = (itemId) => setCheckedItems((current) => {
    const next = new Set(current);
    if (next.has(itemId)) next.delete(itemId);
    else next.add(itemId);
    return next;
  });

  const updateStatus = async () => {
    if (!detail || updating) return;
    const items = detail.items || [];
    if (checkedItems.size !== items.length) {
      setError('Hãy kiểm tra đủ tất cả sản phẩm trong đơn trước khi tiếp tục.');
      return;
    }
    setError('');
    setUpdating(true);
    try {
      if (detail.status === 'confirmed') {
        setDetail(await apiClient.patch(`orders/${detail.id}/status`, { status: 'processing', note: 'Bắt đầu đóng gói' }));
      } else if (detail.status === 'processing') {
        await apiClient.patch(`orders/${detail.id}/status`, { status: 'ready_to_ship', note: 'Đã đóng gói, chờ bàn giao' });
        setDetail(await apiClient.patch(`orders/${detail.id}/status`, { status: 'shipped', note: 'Đã bàn giao vận chuyển' }));
      } else if (detail.status === 'ready_to_ship') {
        setDetail(await apiClient.patch(`orders/${detail.id}/status`, { status: 'shipped', note: 'Đã bàn giao vận chuyển' }));
      }
      await loadOrders();
    } catch (updateError) {
      setError(updateError.message);
      try { setDetail(await apiClient.get(`orders/${detail.id}`)); } catch { /* Keep the last loaded details visible. */ }
      await loadOrders();
    } finally {
      setUpdating(false);
    }
  };

  const nextAction = detail?.status === 'confirmed'
    ? 'Bắt đầu đóng gói'
    : ['processing', 'ready_to_ship'].includes(detail?.status) ? 'Xác nhận bàn giao vận chuyển' : '';
  const currentProgress = detail ? progressFor(detail.status) : 0;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Đơn cần chuẩn bị</h1>
        <button type="button" className="text-sm text-[#0f9d8a] disabled:opacity-50" onClick={loadOrders} disabled={loading}>Tải lại</button>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { id: 'confirmed', label: 'Chờ chuẩn bị', value: counts.confirmed },
          { id: 'packing', label: 'Đang đóng gói', value: counts.packing },
          { id: 'shipped', label: 'Đã bàn giao vận chuyển', value: counts.shipped },
          { id: 'all', label: 'Tổng đơn', value: counts.all },
        ].map((item) => <button key={item.id} type="button" onClick={() => setFilter(item.id)} className={`rounded-xl border bg-[#152427] p-4 text-left transition-colors ${filter === item.id ? 'border-[#0f9d8a]' : 'border-[#24383b]'}`}><p className="text-xs text-[#92a9ad]">{item.label}</p><p className="mt-1 text-xl font-bold">{item.value}</p></button>)}
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((item) => <button key={item.id} type="button" onClick={() => setFilter(item.id)} className={`rounded-lg border px-3 py-2 text-xs ${filter === item.id ? 'border-[#0f9d8a] bg-[#12383a] text-[#48c6b2]' : 'border-[#24383b] text-[#c5d2d2]'}`}>{item.label}</button>)}
      </div>

      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Mã đơn</th><th className="p-3">Khách hàng</th><th className="p-3">Số sản phẩm</th><th className="p-3">Thanh toán</th><th className="p-3">Trạng thái</th><th className="p-3 text-right" /></tr></thead>
          <tbody>
            {!loading && visibleOrders.map((order) => <tr key={order.id} className="border-b border-[#24383b] last:border-0">
              <td className="p-3 font-bold">{formatOrderNumber(order.order_number)}</td>
              <td className="p-3">{order.customer_name || 'Khách vãng lai'}</td>
              <td className="p-3">{order.item_count ?? '—'}</td>
              <td className="p-3">{paymentMethods[order.payment_method] || order.payment_method} – {paymentStatuses[order.payment_status] || order.payment_status}</td>
              <td className="p-3"><span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${statusStyles[order.status] || ''}`}>{statusLabels[order.status] || order.status}</span></td>
              <td className="p-3 text-right"><button type="button" className="rounded-lg bg-[#489f91] px-3 py-1.5 text-xs font-bold text-white hover:bg-[#0f9d8a]" onClick={() => openDetail(order)}>Chi tiết</button></td>
            </tr>)}
            {!loading && visibleOrders.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Không có đơn cần chuẩn bị.</td></tr>}
            {loading && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Đang tải đơn hàng…</td></tr>}
          </tbody>
        </table>
      </div>

      {detailLoading && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 text-sm">Đang tải chi tiết đơn hàng…</div>}

      {detail && !detailLoading && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) setDetail(null); }}>
        <section className="w-full max-w-xl space-y-4 rounded-xl border border-[#24383b] bg-[#152427] p-4">
          <div><h2 className="font-bold">Đơn {formatOrderNumber(detail.order_number)}</h2><p className="mt-1 text-xs text-[#92a9ad]">{detail.customer_name || 'Khách vãng lai'} · {paymentMethods[detail.payment_method] || detail.payment_method} – {paymentStatuses[detail.payment_status] || detail.payment_status}</p></div>
          <div className="divide-y divide-[#24383b]">
            {(detail.items || []).map((item) => <label key={item.id} className="flex cursor-pointer items-center gap-3 py-2.5 text-sm"><input type="checkbox" checked={checkedItems.has(item.id)} onChange={() => toggleItem(item.id)} disabled={!nextAction} /><span className="min-w-0 flex-1"><strong className="block">{item.product_name_snapshot}</strong><span className="block text-xs text-[#92a9ad]">{item.color_snapshot} / {item.size_snapshot}</span></span><span className="shrink-0">× {item.quantity}</span></label>)}
          </div>
          <div className="px-1 pt-1">
            <div className="relative mx-8 h-1 rounded-full bg-[#24383b]"><div className="absolute left-0 top-0 h-1 rounded-full bg-[#0f9d8a]" style={{ width: `${currentProgress * 50}%` }} />{[0, 1, 2].map((step) => <span key={step} className={`absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ${currentProgress >= step ? 'bg-[#0f9d8a]' : 'bg-[#24383b]'}`} style={{ left: `${step * 50}%` }} />)}</div>
            <div className="mt-3 flex justify-between text-[10px] text-[#92a9ad]"><span>Chờ chuẩn bị</span><span>Đóng gói</span><span>Bàn giao</span></div>
          </div>
          <div className="flex justify-end gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2 text-sm" onClick={() => setDetail(null)}>Đóng</button>{nextAction && <button type="button" disabled={updating} className="rounded-lg bg-[#489f91] px-4 py-2 text-sm font-bold text-white disabled:opacity-60" onClick={updateStatus}>{updating ? 'Đang cập nhật…' : nextAction}</button>}</div>
        </section>
      </div>}
    </div>
  );
};

export default Orders;
