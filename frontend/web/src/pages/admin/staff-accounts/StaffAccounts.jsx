import React, { useEffect, useState } from 'react';

const mockStaff = [
  { name: 'Hoàng Thị Mai', email: 'mai@virtufit.vn', phone: '0901111222', role: 'Sales Staff', active: true },
  { name: 'Bùi Tuấn Kiệt', email: 'kiet@virtufit.vn', phone: '0902222333', role: 'Warehouse Staff', active: true },
  { name: 'Ngô Thanh Vy', email: 'vy@virtufit.vn', phone: '0903333444', role: 'Designer', active: true },
];

const StaffAccounts = () => {
  const [staff, setStaff] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('adminStaff')) || mockStaff;
    } catch {
      return mockStaff;
    }
  });
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', role: 'Sales Staff' });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    localStorage.setItem('adminStaff', JSON.stringify(staff));
  }, [staff]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const normalizedEmail = formData.email.trim().toLowerCase();
    if (staff.some((member) => member.email.toLowerCase() === normalizedEmail)) {
      setFormError('Email này đã được sử dụng.');
      return;
    }

    setStaff((currentStaff) => [...currentStaff, {
      ...formData,
      name: formData.name.trim(),
      email: normalizedEmail,
      phone: formData.phone.trim(),
      active: true,
    }]);
    setFormData({ name: '', email: '', phone: '', role: 'Sales Staff' });
    setFormError('');
  };

  const updateRole = (email, role) => {
    setStaff((currentStaff) => currentStaff.map((member) => member.email === email ? { ...member, role } : member));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl h-fit">
        <h3 className="font-bold text-base mb-4">Tạo tài khoản nhân viên</h3>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Họ và tên</label>
            <input required value={formData.name} onChange={(event) => setFormData({ ...formData, name: event.target.value })} placeholder="Nguyễn Văn A" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Email</label>
            <input type="email" required value={formData.email} onChange={(event) => setFormData({ ...formData, email: event.target.value })} placeholder="nv@virtufit.vn" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Số điện thoại</label>
            <input type="tel" value={formData.phone} onChange={(event) => setFormData({ ...formData, phone: event.target.value })} placeholder="09xxxxxxxx" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Vai trò</label>
            <select value={formData.role} onChange={(event) => setFormData({ ...formData, role: event.target.value })} className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]">
              <option>Sales Staff</option>
              <option>Warehouse Staff</option>
              <option>Designer</option>
            </select>
          </div>
          {formError && <p role="alert" className="text-xs text-[#e5484d]">{formError}</p>}
          <button type="submit" className="w-full bg-[#5b4bff] text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-[#4a3ecc] mt-2">
            Tạo tài khoản
          </button>
        </form>
      </div>
      
      <div className="lg:col-span-2 bg-[#181c30] border border-[#262b45] rounded-2xl overflow-x-auto h-fit">
        <table className="w-full text-left min-w-[400px]">
          <thead>
            <tr className="border-b border-[#262b45] text-[#9aa2c0] text-xs">
              <th className="p-4 font-semibold">Nhân viên</th>
              <th className="p-4 font-semibold">Vai trò (phân quyền)</th>
              <th className="p-4 font-semibold">Trạng thái</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {staff.map((s) => (
              <tr key={s.email} className="border-b border-[#262b45] last:border-0">
                <td className="p-4"><b>{s.name}</b><br/><span className="text-[#9aa2c0] text-xs">{s.email}{s.phone && ` · ${s.phone}`}</span></td>
                <td className="p-4">
                  <select value={s.role} onChange={(event) => updateRole(s.email, event.target.value)} aria-label={`Vai trò của ${s.name}`} className="bg-[#0f1220] border border-[#262b45] rounded-lg px-3 py-1.5 text-sm outline-none focus:border-[#5b4bff]">
                    <option>Sales Staff</option>
                    <option>Warehouse Staff</option>
                    <option>Designer</option>
                  </select>
                </td>
                <td className="p-4"><span className="bg-[#0f2e24] text-[#12a66a] px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap">{s.active ? 'Hoạt động' : 'Đã khóa'}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StaffAccounts;