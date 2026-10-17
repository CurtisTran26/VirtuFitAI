import React, { useState } from 'react';

const mockCustomers = [
  { name: 'Nguyễn Minh Anh', email: 'anh.nm@mail.com', phone: '0901234567', orders: 12, active: true },
  { name: 'Trần Bảo Ngọc', email: 'ngoc.tb@mail.com', phone: '0912345678', orders: 7, active: true },
  { name: 'Lê Hoàng Nam', email: 'nam.lh@mail.com', phone: '0987654321', orders: 0, active: false },
  { name: 'Phạm Thu Hà', email: 'ha.pt@mail.com', phone: '0933445566', orders: 21, active: true },
];

const CustomerAccounts = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
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
        <select className="bg-[#181c30] border border-[#262b45] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#5b4bff] text-sm">
          <option>Tất cả trạng thái</option>
          <option>Hoạt động</option>
          <option>Đã khóa</option>
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
            {mockCustomers.map((c, i) => (
              <tr key={i} className="border-b border-[#262b45] last:border-0">
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
                  <button className={`w-11 h-6 rounded-full relative transition-colors ${c.active ? 'bg-[#12a66a]' : 'bg-[#262b45]'}`}>
                    <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${c.active ? 'translate-x-5' : 'translate-x-0'}`}></span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CustomerAccounts;