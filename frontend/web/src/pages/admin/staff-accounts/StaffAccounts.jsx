import React from 'react';

const mockStaff = [
  { name: 'Hoàng Thị Mai', email: 'mai@virtufit.vn', role: 'Sales Staff' },
  { name: 'Bùi Tuấn Kiệt', email: 'kiet@virtufit.vn', role: 'Warehouse Staff' },
  { name: 'Ngô Thanh Vy', email: 'vy@virtufit.vn', role: 'Designer' },
];

const StaffAccounts = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl h-fit">
        <h3 className="font-bold text-base mb-4">Tạo tài khoản nhân viên</h3>
        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Họ và tên</label>
            <input required placeholder="Nguyễn Văn A" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Email</label>
            <input type="email" required placeholder="nv@virtufit.vn" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Vai trò</label>
            <select className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]">
              <option>Sales Staff</option>
              <option>Warehouse Staff</option>
              <option>Designer</option>
            </select>
          </div>
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
            {mockStaff.map((s, i) => (
              <tr key={i} className="border-b border-[#262b45] last:border-0">
                <td className="p-4"><b>{s.name}</b><br/><span className="text-[#9aa2c0] text-xs">{s.email}</span></td>
                <td className="p-4">
                  <select defaultValue={s.role} className="bg-[#0f1220] border border-[#262b45] rounded-lg px-3 py-1.5 text-sm outline-none focus:border-[#5b4bff]">
                    <option>Sales Staff</option>
                    <option>Warehouse Staff</option>
                    <option>Designer</option>
                  </select>
                </td>
                <td className="p-4"><span className="bg-[#0f2e24] text-[#12a66a] px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap">Hoạt động</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StaffAccounts;