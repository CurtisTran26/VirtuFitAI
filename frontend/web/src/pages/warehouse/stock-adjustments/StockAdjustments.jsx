import React, { useState, useMemo } from 'react';

const initialInventory = [
  { id: 1, name: 'Áo sơ mi linen', color: 'Trắng', size: 'M', stock: 24 },
  { id: 2, name: 'Áo sơ mi linen', color: 'Trắng', size: 'L', stock: 4 },
  { id: 3, name: 'Đầm midi hoa', color: 'Đỏ đô', size: 'S', stock: 0 },
  { id: 4, name: 'Đầm midi hoa', color: 'Đỏ đô', size: 'M', stock: 12 },
  { id: 5, name: 'Quần jeans slim', color: 'Xanh navy', size: 'L', stock: 31 },
  { id: 6, name: 'Áo khoác bomber', color: 'Đen', size: 'XL', stock: 3 },
  { id: 7, name: 'Áo khoác bomber', color: 'Đen', size: 'M', stock: 18 },
  { id: 8, name: 'Váy xếp ly', color: 'Be', size: 'S', stock: 9 },
];

const StockAdjustments = () => {
  const [inventoryList, setInventoryList] = useState(initialInventory);
  const [filter, setFilter] = useState('Tất cả');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [adjustForm, setAdjustForm] = useState({ type: '+', quantity: 1, reason: 'Nhập hàng mới' });

  const stats = useMemo(() => {
    let total = 0, inStock = 0, lowStock = 0, outOfStock = 0;
    inventoryList.forEach(item => {
      total += item.stock;
      if (item.stock === 0) outOfStock++;
      else if (item.stock <= 5) lowStock++;
      else inStock++;
    });
    return { total, inStock, lowStock, outOfStock };
  }, [inventoryList]);

  const getStatus = (stock) => {
    if (stock === 0) return { label: 'Hết hàng', color: 'text-[#e5484d] bg-[#3a1a1e]' };
    if (stock <= 5) return { label: 'Sắp hết', color: 'text-[#f5a623] bg-[#3d2b15]' };
    return { label: 'Còn hàng', color: 'text-[#12a66a] bg-[#0f2e24]' };
  };

  const handleOpenAdjust = (item) => {
    setSelectedItem(item);
    setAdjustForm({ type: '+', quantity: 1, reason: 'Nhập hàng mới' });
    setIsModalOpen(true);
  };

  const handleAdjustSubmit = (e) => {
    e.preventDefault();
    if (!selectedItem) return;

    const qty = Number(adjustForm.quantity);
    if (qty <= 0) return alert("Số lượng phải lớn hơn 0");

    setInventoryList(prev => prev.map(item => {
      if (item.id === selectedItem.id) {
        let newStock = item.stock;
        if (adjustForm.type === '+') newStock += qty;
        else if (adjustForm.type === '-') newStock = Math.max(0, newStock - qty);
        else newStock = qty;
        return { ...item, stock: newStock };
      }
      return item;
    }));
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-white text-xl font-bold">Danh sách tồn kho</h1>
        <select 
          className="bg-[#152427] border border-[#24383b] text-white px-4 py-2 rounded-xl text-sm focus:outline-none"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="Tất cả">Tất cả</option>
          <option value="Còn hàng">Còn hàng</option>
          <option value="Sắp hết">Sắp hết</option>
          <option value="Hết hàng">Hết hàng</option>
        </select>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl">
          <p className="text-[#92a9ad] text-xs font-semibold mb-2">Tổng tồn</p>
          <p className="text-white text-3xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl">
          <p className="text-[#92a9ad] text-xs font-semibold mb-2">Còn hàng</p>
          <p className="text-white text-3xl font-bold">{stats.inStock}</p>
        </div>
        <div className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl">
          <p className="text-[#92a9ad] text-xs font-semibold mb-2">Sắp hết (≤5)</p>
          <p className="text-white text-3xl font-bold">{stats.lowStock}</p>
        </div>
        <div className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl">
          <p className="text-[#92a9ad] text-xs font-semibold mb-2">Hết hàng</p>
          <p className="text-white text-3xl font-bold">{stats.outOfStock}</p>
        </div>
      </div>

      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[700px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-5 font-semibold">Sản phẩm</th>
              <th className="p-5 font-semibold">Màu</th>
              <th className="p-5 font-semibold">Size</th>
              <th className="p-5 font-semibold">Tồn</th>
              <th className="p-5 font-semibold">Trạng thái</th>
              <th className="p-5"></th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {inventoryList.map((item) => {
              const status = getStatus(item.stock);
              if (filter !== 'Tất cả' && filter !== status.label) return null;

              return (
                <tr key={item.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                  <td className="p-5 text-white font-semibold">{item.name}</td>
                  <td className="p-5 text-[#92a9ad]">{item.color}</td>
                  <td className="p-5 text-[#92a9ad]">{item.size}</td>
                  <td className="p-5 text-white font-bold">{item.stock}</td>
                  <td className="p-5">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${status.color}`}>
                      {status.label}
                    </span>
                  </td>
                  <td className="p-5 text-right">
                    <button onClick={() => handleOpenAdjust(item)} className="border border-[#24383b] text-[#92a9ad] px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors">
                      Điều chỉnh
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {isModalOpen && selectedItem && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-fade-in">
          <div className="bg-[#152427] border border-[#24383b] p-6 rounded-2xl w-full max-w-md shadow-2xl">
            <h2 className="text-white text-lg font-bold mb-1">Điều chỉnh tồn kho</h2>
            <p className="text-[#92a9ad] text-xs mb-6">
              {selectedItem.name} • {selectedItem.color} / {selectedItem.size} • Tồn hiện tại: {selectedItem.stock}
            </p>
            
            <form onSubmit={handleAdjustSubmit} className="space-y-4">
              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Loại điều chỉnh</label>
                <select className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] appearance-none"
                  value={adjustForm.type} onChange={e => setAdjustForm({...adjustForm, type: e.target.value})}>
                  <option value="+">Nhập thêm (+)</option>
                  <option value="-">Xuất bớt (-)</option>
                  <option value="=">Kiểm kê thực tế (Ghi đè)</option>
                </select>
              </div>

              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Số lượng</label>
                <input required type="number" min="1" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a]"
                  value={adjustForm.quantity} onChange={e => setAdjustForm({...adjustForm, quantity: e.target.value})} />
              </div>

              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Lý do</label>
                <select className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] appearance-none"
                  value={adjustForm.reason} onChange={e => setAdjustForm({...adjustForm, reason: e.target.value})}>
                  <option value="Nhập hàng mới">Nhập hàng mới</option>
                  <option value="Khách trả hàng">Khách trả hàng</option>
                  <option value="Hàng lỗi / Hư hỏng">Hàng lỗi / Hư hỏng</option>
                  <option value="Sai lệch kiểm đếm">Sai lệch kiểm đếm</option>
                  <option value="Khác">Khác...</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="border border-[#24383b] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#24383b] transition-colors">Hủy</button>
                <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors shadow-lg">Xác nhận</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockAdjustments;