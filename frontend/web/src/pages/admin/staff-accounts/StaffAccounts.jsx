import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const roleLabels = { admin: 'Quản trị viên', sales_staff: 'Nhân viên bán hàng', warehouse_staff: 'Nhân viên kho', designer: 'Thiết kế' };
const inputClass = 'w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]';
const initialForm = { full_name: '', account: '', password: '', role: 'sales_staff' };

const StaffAccounts = () => {
  const [staff, setStaff] = useState([]);
  const [roles, setRoles] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const loadStaff = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [result, roleResult] = await Promise.all([apiClient.get('admin/users?page=1&limit=100'), apiClient.get('admin/roles')]);
      setStaff((result.items || []).filter((user) => !['customer', 'admin'].includes(user.role)));
      setRoles((roleResult.items || []).filter((role) => !['customer', 'admin'].includes(role.name)));
    }
    catch (loadError) { setError(loadError.message); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { loadStaff(); }, [loadStaff]);

  const createStaff = async (event) => {
    event.preventDefault(); setError('');
    const fullName = String(form.full_name ?? '').trim();
    const account = String(form.account ?? form.phone ?? '').trim();
    if (!fullName || !account || !form.password) {
      setError('Vui lòng nhập họ tên, tài khoản và mật khẩu.');
      return;
    }
    try { await apiClient.post('admin/users', { ...form, full_name: fullName, account, password: String(form.password) }); setForm({ ...initialForm }); await loadStaff(); }
    catch (createError) { setError(createError.message); }
  };

  const updateRole = async (member, role) => {
    setError('');
    try { await apiClient.patch(`admin/users/${member.id}/role`, { role }); await loadStaff(); }
    catch (updateError) { setError(updateError.message); }
  };

  const updateStatus = async (member) => {
    setError('');
    try { await apiClient.patch(`admin/users/${member.id}/status?is_active=${!member.is_active}`); await loadStaff(); }
    catch (updateError) { setError(updateError.message); }
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <form onSubmit={createStaff} className="h-fit space-y-4 rounded-2xl border border-[#262b45] bg-[#181c30] p-5"><h2 className="font-bold">Tạo tài khoản nhân viên</h2><label className="block text-xs text-[#9aa2c0]">Họ và tên<input className={`${inputClass} mt-2`} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></label><label className="block text-xs text-[#9aa2c0]">Tài khoản<input className={`${inputClass} mt-2`} type="text" autoComplete="username" value={form.account} onChange={(e) => setForm({ ...form, account: e.target.value })} placeholder="Warehouse@test" maxLength="20" required /></label><label className="block text-xs text-[#9aa2c0]">Mật khẩu ban đầu<input className={`${inputClass} mt-2`} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} maxLength="72" required /></label><label className="block text-xs text-[#9aa2c0]">Vai trò<select className={`${inputClass} mt-2`} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>{roles.map((role) => <option key={role.name} value={role.name}>{roleLabels[role.name] || role.description || role.name}</option>)}</select></label>{error && <p role="alert" className="text-xs text-red-300">{error}</p>}<button className="w-full rounded-lg bg-[#5b4bff] px-4 py-2.5 text-sm font-bold" type="submit">Tạo tài khoản</button></form>
      <div className="h-fit overflow-x-auto rounded-2xl border border-[#262b45] bg-[#181c30] lg:col-span-2"><div className="flex items-center justify-between p-4"><h2 className="font-bold">Tài khoản nhân viên</h2><button className="text-sm text-[#aaa2ff]" onClick={loadStaff}>Tải lại</button></div><table className="w-full min-w-[650px] text-left text-sm"><thead><tr className="border-y border-[#262b45] text-xs text-[#9aa2c0]"><th className="p-3">Nhân viên</th><th className="p-3">Vai trò</th><th className="p-3">Trạng thái</th><th className="p-3">Tài khoản</th></tr></thead><tbody>{!loading && staff.map((member) => <tr key={member.id} className="border-b border-[#262b45] last:border-0"><td className="p-3 font-semibold">{member.full_name}</td><td className="p-3"><select className="rounded-lg border border-[#262b45] bg-[#0f1220] px-2 py-1.5" value={member.role} onChange={(e) => updateRole(member, e.target.value)}>{roles.map((role) => <option key={role.name} value={role.name}>{roleLabels[role.name] || role.name}</option>)}</select></td><td className="p-3"><button className={`rounded-full px-3 py-1 text-xs font-bold ${member.is_active ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a1a1e] text-[#e5484d]'}`} onClick={() => updateStatus(member)}>{member.is_active ? 'Hoạt động · khóa' : 'Đã khóa · mở'}</button></td><td className="p-3">{member.account || member.phone}</td></tr>)}{!loading && staff.length === 0 && <tr><td className="p-6 text-center text-[#9aa2c0]" colSpan="4">Chưa có tài khoản nhân viên.</td></tr>}{loading && <tr><td className="p-6 text-center text-[#9aa2c0]" colSpan="4">Đang tải…</td></tr>}</tbody></table></div>
    </div>
  );
};

export default StaffAccounts;
