import React, { useEffect, useState } from 'react';

const mockCustomers = [
  { name: 'Nguyễn Minh Anh', email: 'anh.nm@mail.com', phone: '0901234567', orders: 12, active: true },
  { name: 'Trần Bảo Ngọc', email: 'ngoc.tb@mail.com', phone: '0912345678', orders: 7, active: true },
  { name: 'Lê Hoàng Nam', email: 'nam.lh@mail.com', phone: '0987654321', orders: 0, active: false },
  { name: 'Phạm Thu Hà', email: 'ha.pt@mail.com', phone: '0933445566', orders: 21, active: true },
];

const CustomerAccounts = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [customers, setCustomers] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('adminCustomers')) || mockCustomers;
    } catch {
      return mockCustomers;
    }
  });
  const [pendingCustomer, setPendingCustomer] = useState(null);

  useEffect(() => {
    localStorage.setItem('adminCustomers', JSON.stringify(customers));
  }, [customers]);

  const filteredCustomers = customers.filter((customer) => {
    const query = searchTerm.trim().toLowerCase();
    const matchesSearch = !query || [customer.name, customer.email, customer.phone].some((value) => value.toLowerCase().includes(query));
    const matchesStatus = statusFilter === 'all' || (statusFilter === 'active' ? customer.active : !customer.active);
    return matchesSearch && matchesStatus;
  });

  const confirmStatusChange = () => {
    if (!pendingCustomer) return;
    setCustomers((currentCustomers) => currentCustomers.map((customer) => (
      customer.email === pendingCustomer.email ? { ...customer, active: !customer.active } : customer
    )));
    setPendingCustomer(null);
  };
  
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <input 
          type="text" 
          placeholder="🔍 Tìm tên / email / SĐT" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 min-w-[200px] bg-[#181c30] border border-[#262b45] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#5b4bff] text-sm" 
        />
        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="bg-[#181c30] border border-[#262b45] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#5b4bff] text-sm">
          <option value="all">Tất cả trạng thái</option>
          <option value="active">Hoạt động</option>
          <option value="locked">Đã khóa</option>
        </select>
      </div>
      
      <div className="bg-[#181c30] border border-[#262b45] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[620px]">
          <thead>
            <tr className="border-b border-[#262b45] text-[#9aa2c0] text-xs">
              <th className="p-4 font-semibold">Khách hàng</th>
              <th className="p-4 font-semibold">Email</th>
              <th className="p-4 font-semibold">SĐT</th>
              <th className="p-4 font-semibold">Đơn</th>
              <th className="p-4 font-semibold">Trạng thái</th>
              <th className="p-4">Khóa/Mở</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {filteredCustomers.map((c) => (
              <tr key={c.email} className="border-b border-[#262b45] last:border-0">
                <td className="p-4 font-bold">{c.name}</td>
                <td className="p-4">{c.email}</td>
                <td className="p-4">{c.phone}</td>
                <td className="p-4">{c.orders}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${c.active ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a1a1e] text-[#e5484d]'}`}>
                    {c.active ? 'Hoạt động' : 'Đã khóa'}
                  </span>
                </td>
                <td className="p-4">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={c.active}
                    aria-label={`${c.active ? 'Khóa' : 'Mở khóa'} tài khoản ${c.name}`}
                    onClick={() => setPendingCustomer(c)}
                    className={`w-11 h-6 rounded-full relative transition-colors ${c.active ? 'bg-[#12a66a]' : 'bg-[#262b45]'}`}
                  >
                    <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${c.active ? 'translate-x-5' : 'translate-x-0'}`}></span>
                  </button>
                </td>
              </tr>
            ))}
            {filteredCustomers.length === 0 && (
              <tr><td colSpan="6" className="p-8 text-center text-sm text-[#9aa2c0]">Không tìm thấy tài khoản khách hàng.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {pendingCustomer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) setPendingCustomer(null); }}>
          <section role="dialog" aria-modal="true" aria-labelledby="customer-status-title" className="w-full max-w-sm rounded-xl border border-[#262b45] bg-[#181c30] p-5 shadow-2xl">
            <h2 id="customer-status-title" className="text-base font-bold">{pendingCustomer.active ? 'Khóa tài khoản?' : 'Mở khóa tài khoản?'}</h2>
            <p className="mt-2 text-sm text-[#9aa2c0]">
              {pendingCustomer.active
                ? `${pendingCustomer.name} sẽ không thể đăng nhập cho đến khi được mở khóa.`
                : `Khôi phục quyền truy cập cho ${pendingCustomer.name}?`}
            </p>
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" onClick={() => setPendingCustomer(null)} className="rounded-lg border border-[#262b45] px-4 py-2 text-xs font-bold text-[#9aa2c0] hover:bg-[#262b45]">Hủy</button>
              <button type="button" onClick={confirmStatusChange} className="rounded-lg bg-[#5b4bff] px-4 py-2 text-xs font-bold text-white hover:bg-[#4a3ecc]">Xác nhận</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
};

export default CustomerAccounts;