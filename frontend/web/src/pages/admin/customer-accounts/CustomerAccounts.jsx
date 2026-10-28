import React, { useCallback, useEffect, useMemo, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const inputClass = 'rounded-lg border border-[#262b45] bg-[#111526] px-3 py-2 text-sm text-white outline-none focus:border-[#5b4bff]';

const CustomerAccounts = () => {
  const [customers, setCustomers] = useState([]);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [pending, setPending] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const loadCustomers = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiClient.get('admin/users?page=1&limit=100&role=customer');
      setCustomers(result.items || []);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadCustomers(); }, [loadCustomers]);

  const updateStatus = async () => {
    if (!pending || saving) return;
    setSaving(true);
    setError('');
    try {
      const isActive = !pending.is_active;
      await apiClient.patch(`admin/users/${pending.id}/status?is_active=${isActive}`);
      setCustomers((current) => current.map((customer) => customer.id === pending.id ? { ...customer, is_active: isActive } : customer));
      setPending(null);
    } catch (updateError) {
      setError(updateError.message);
    } finally {
      setSaving(false);
    }
  };

  const visible = useMemo(() => customers.filter((customer) => {
    const matchesQuery = `${customer.full_name || ''} ${customer.email || ''} ${customer.phone || ''}`.toLowerCase().includes(query.trim().toLowerCase());
    const matchesStatus = statusFilter === 'all' || (statusFilter === 'active' ? customer.is_active : !customer.is_active);
    return matchesQuery && matchesStatus;
  }), [customers, query, statusFilter]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Tài khoản khách hàng</h1>
        <div className="flex flex-wrap items-center gap-2">
          <input className={`${inputClass} w-full sm:w-64`} placeholder="Tìm tên / email / SĐT" value={query} onChange={(event) => setQuery(event.target.value)} />
          <select className={inputClass} value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} aria-label="Lọc trạng thái khách hàng">
            <option value="all">Tất cả</option><option value="active">Hoạt động</option><option value="locked">Đã khóa</option>
          </select>
          <button type="button" className="px-2 text-sm text-[#aaa2ff] disabled:opacity-50" onClick={loadCustomers} disabled={loading}>Tải lại</button>
        </div>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}

      <div className="overflow-x-auto rounded-xl border border-[#262b45] bg-[#181c30]">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead><tr className="border-b border-[#262b45] text-xs text-[#9aa2c0]"><th className="p-3">Khách hàng</th><th className="p-3">Email</th><th className="p-3">SĐT</th><th className="p-3">Đơn</th><th className="p-3">Trạng thái</th><th className="p-3 text-center">Khóa / Mở</th></tr></thead>
          <tbody>
            {!loading && visible.map((customer) => <tr key={customer.id} className="border-b border-[#262b45] last:border-0">
              <td className="p-3 font-semibold">{customer.full_name}</td>
              <td className="p-3 text-[#9aa2c0]">{customer.email || '—'}</td>
              <td className="p-3">{customer.phone}</td>
              <td className="p-3">{customer.order_count ?? 0}</td>
              <td className="p-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${customer.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>{customer.is_active ? 'Hoạt động' : 'Đã khóa'}</span></td>
              <td className="p-3 text-center"><button type="button" role="switch" aria-checked={customer.is_active} aria-label={`${customer.is_active ? 'Khóa' : 'Mở khóa'} tài khoản ${customer.full_name}`} onClick={() => setPending(customer)} className={`relative inline-flex h-5 w-10 items-center rounded-full transition-colors ${customer.is_active ? 'bg-emerald-700' : 'bg-[#36394a]'}`}><span className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${customer.is_active ? 'translate-x-5' : 'translate-x-1'}`} /></button></td>
            </tr>)}
            {!loading && visible.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-[#9aa2c0]">Không có tài khoản khách hàng phù hợp.</td></tr>}
            {loading && <tr><td colSpan="6" className="p-8 text-center text-[#9aa2c0]">Đang tải tài khoản…</td></tr>}
          </tbody>
        </table>
      </div>

      {pending && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) setPending(null); }}>
        <section role="dialog" aria-modal="true" aria-labelledby="customer-status-title" className="w-full max-w-sm rounded-xl border border-[#262b45] bg-[#181c30] p-5 shadow-2xl">
          <h2 id="customer-status-title" className="font-bold">{pending.is_active ? 'Khóa tài khoản?' : 'Mở khóa tài khoản?'}</h2>
          <p className="mt-2 text-sm text-[#9aa2c0]">{pending.is_active ? `${pending.full_name} sẽ không thể đăng nhập cho đến khi được mở khóa.` : `Khôi phục quyền truy cập cho ${pending.full_name}?`}</p>
          <div className="mt-5 flex justify-end gap-2"><button type="button" disabled={saving} className="rounded-lg border border-[#262b45] px-4 py-2 disabled:opacity-50" onClick={() => setPending(null)}>Hủy</button><button type="button" disabled={saving} className="rounded-lg bg-[#5b4bff] px-4 py-2 font-bold disabled:opacity-50" onClick={updateStatus}>{saving ? 'Đang lưu…' : 'Xác nhận'}</button></div>
        </section>
      </div>}
    </div>
  );
};

export default CustomerAccounts;
