import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const inputClass = 'w-full rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none focus:border-[#0f9d8a]';
const formatReturnCode = (id) => `RT-${id.slice(0, 8).toUpperCase()}`;
const formatOrderCode = (number) => number ? `#${number}` : '—';

const statusFor = (item) => {
  if (item.status === 'requested') return { label: 'Chờ tiếp nhận', style: 'bg-amber-500/10 text-amber-300' };
  if (item.status === 'rejected') return { label: 'Không đạt – từ chối', style: 'bg-red-500/10 text-red-300' };
  if (item.restocked) return { label: 'Đã nhập lại kho', style: 'bg-emerald-500/10 text-emerald-300' };
  return { label: 'Đã chấp nhận', style: 'bg-emerald-500/10 text-emerald-300' };
};

const Returns = () => {
  const [returns, setReturns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [outcome, setOutcome] = useState('accepted');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const loadReturns = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiClient.get('returns?page=1&limit=100');
      setReturns(result.items || []);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadReturns(); }, [loadReturns]);

  const openInspection = async (item) => {
    setError('');
    try {
      const result = await apiClient.get(`returns/${item.id}`);
      setSelected(result);
      setOutcome('accepted');
      setNote('');
    } catch (loadError) {
      setError(loadError.message);
    }
  };

  const inspect = async (event) => {
    event.preventDefault();
    if (!selected || saving) return;
    setError('');
    setSaving(true);
    try {
      await apiClient.post(`returns/${selected.id}/inspect`, {
        outcome,
        note: note.trim(),
        items: (selected.items || []).map((item) => ({
          return_item_id: item.id,
          condition_note: note.trim(),
          restock: outcome === 'accepted',
        })),
      });
      setSelected(null);
      await loadReturns();
    } catch (inspectError) {
      setError(inspectError.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Tiếp nhận &amp; kiểm tra hàng trả</h1>
        <button type="button" className="text-sm text-[#0f9d8a] disabled:opacity-50" onClick={loadReturns} disabled={loading}>Tải lại</button>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}

      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Mã trả</th><th className="p-3">Đơn gốc</th><th className="p-3">Sản phẩm</th><th className="p-3">Lý do</th><th className="p-3">Trạng thái</th><th className="p-3 text-right" /></tr></thead>
          <tbody>
            {!loading && returns.map((item) => {
              const status = statusFor(item);
              return <tr key={item.id} className="border-b border-[#24383b] last:border-0">
                <td className="p-3 font-semibold">{formatReturnCode(item.id)}</td>
                <td className="p-3">{formatOrderCode(item.order_number)}</td>
                <td className="p-3">{item.product_summary || '—'}</td>
                <td className="p-3">{item.reason}</td>
                <td className="p-3"><span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${status.style}`}>{status.label}</span></td>
                <td className="p-3 text-right">{item.status === 'requested' && <button type="button" className="rounded-lg bg-[#489f91] px-3 py-1.5 text-xs font-bold text-white hover:bg-[#0f9d8a]" onClick={() => openInspection(item)}>Kiểm tra</button>}</td>
              </tr>;
            })}
            {!loading && returns.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Chưa có yêu cầu trả hàng từ khách.</td></tr>}
            {loading && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Đang tải yêu cầu trả hàng…</td></tr>}
          </tbody>
        </table>
      </div>

      {selected && <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/70 p-4">
        <form onSubmit={inspect} className="my-auto w-full max-w-md space-y-3 rounded-xl border border-[#24383b] bg-[#152427] p-4">
          <h2 className="font-bold">Kiểm tra hàng trả {formatReturnCode(selected.id)}</h2>
          <p className="text-xs text-[#92a9ad]">{selected.items?.map((item) => `${item.product_name_snapshot} (${item.color_snapshot}/${item.size_snapshot})`).join(', ')} · Lý do: {selected.reason}</p>
          <label className="block text-xs text-[#92a9ad]">Kết quả<select className={`${inputClass} mt-1`} value={outcome} onChange={(event) => setOutcome(event.target.value)}><option value="accepted">Đạt – nhập lại kho</option><option value="rejected">Không đạt – từ chối</option></select></label>
          <label className="block text-xs text-[#92a9ad]">Ghi chú<textarea className={`${inputClass} mt-1`} rows="3" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Tình trạng sản phẩm, tem mác…" required /></label>
          <div className="flex justify-end gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2" onClick={() => setSelected(null)}>Hủy</button><button type="submit" disabled={saving} className="rounded-lg bg-[#489f91] px-4 py-2 text-sm font-bold text-white disabled:opacity-60">{saving ? 'Đang lưu…' : 'Xác nhận kiểm tra'}</button></div>
        </form>
      </div>}
    </div>
  );
};

export default Returns;
