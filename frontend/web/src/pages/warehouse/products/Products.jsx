import React, { useState } from 'react';

const mockProducts = [
  { id: 1, name: 'Áo sơ mi linen', sku: 'VF-AS-001', cat: 'Áo', price: '459.000₫', stock: 28, active: true, icon: '👔' },
  { id: 2, name: 'Đầm midi hoa', sku: 'VF-DM-014', cat: 'Váy / Đầm', price: '689.000₫', stock: 12, active: true, icon: '👗' },
  { id: 3, name: 'Quần jeans slim', sku: 'VF-QJ-007', cat: 'Quần', price: '539.000₫', stock: 5, active: true, icon: '👖' },
  { id: 4, name: 'Áo khoác bomber', sku: 'VF-AK-003', cat: 'Áo khoác', price: '799.000₫', stock: 21, active: true, icon: '🧥' },
  { id: 5, name: 'Váy xếp ly', sku: 'VF-VX-009', cat: 'Váy / Đầm', price: '419.000₫', stock: 0, active: false, icon: '👗' }
];

const Products = () => {
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 justify-between items-center mb-2">
        <input 
          type="text" 
          placeholder="🔍 Tìm tên / SKU" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-[#152427] border border-[#24383b] text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-[#0f9d8a] min-w-[260px] text-sm" 
        />
        <button className="bg-[#0f9d8a] text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] shadow-lg transition-colors">
          ＋ Thêm sản phẩm
        </button>
      </div>

      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[620px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-4 font-semibold">Sản phẩm</th>
              <th className="p-4 font-semibold">SKU</th>
              <th className="p-4 font-semibold">Danh mục</th>
              <th className="p-4 font-semibold">Giá</th>
              <th className="p-4 font-semibold">Tồn</th>
              <th className="p-4 font-semibold">Trạng thái</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {mockProducts.map((p) => (
              <tr key={p.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 font-bold flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#12383a] flex items-center justify-center text-xl">{p.icon}</div>
                  {p.name}
                </td>
                <td className="p-4">{p.sku}</td>
                <td className="p-4">{p.cat}</td>
                <td className="p-4">{p.price}</td>
                <td className="p-4 font-bold">{p.stock}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${p.active ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a1a1e] text-[#e5484d]'}`}>
                    {p.active ? 'Đang bán' : 'Ngừng bán'}
                  </span>
                </td>
                <td className="p-4">
                  <button className="border border-[#24383b] text-[#92a9ad] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors">
                    Sửa
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

export default Products;