import React, { useState } from 'react';

const mockStock = [
  { id: 1, name: 'Áo sơ mi linen', color: 'Trắng', size: 'M', stock: 24, status: 'Còn hàng', badge: 'bg-[#0f2e24] text-[#12a66a]' },
  { id: 2, name: 'Áo sơ mi linen', color: 'Trắng', size: 'L', stock: 4, status: 'Sắp hết', badge: 'bg-[#3a2e12] text-[#e8930c]' },
  { id: 3, name: 'Đầm midi hoa', color: 'Đỏ đô', size: 'S', stock: 0, status: 'Hết hàng', badge: 'bg-[#3a1a1e] text-[#e5484d]' },
  { id: 4, name: 'Đầm midi hoa', color: 'Đỏ đô', size: 'M', stock: 12, status: 'Còn hàng', badge: 'bg-[#0f2e24] text-[#12a66a]' },
];

const StockAdjustments = () => {
  const [stockList, setStockList] = useState(mockStock);
  const [filter, setFilter] = useState('all');
  
  // Trạng thái Modal
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  // Trạng thái Form điều chỉnh
  const [adjustType, setAdjustType] = useState('1'); // 1 = Nhập, -1 = Xuất
  const [adjustQty, setAdjustQty] = useState(1);
  const [adjustReason, setAdjustReason] = useState('Nhập hàng mới');

  const openModal = (item) => {
    setSelectedItem(item);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedItem(null);
    setAdjustQty(1);
    setAdjustType('1');
    setAdjustReason('Nhập hàng mới');
  };

  const handleAdjustSubmit = (e) => {
    e.preventDefault();
    if (!selectedItem) return;

    // Logic giả lập cập nhật lại state tồn kho (Sau này sẽ gọi API ở đây)
    const updatedList = stockList.map(item => {
      if (item.id === selectedItem.id) {
        const change = adjustType === '1' ? Number(adjustQty) : -Number(adjustQty);
        const newStock = Math.max(0, item.stock + change);
        
        let newStatus = 'Còn hàng';
        let newBadge = 'bg-[#0f2e24] text-[#12a66a]';
        
        if (newStock === 0) {
          newStatus = 'Hết hàng';
          newBadge = 'bg-[#3a1a1e] text-[#e5484d]';
        } else if (newStock <= 5) {
          newStatus = 'Sắp hết';
          newBadge = 'bg-[#3a2e12] text-[#e8930c]';
        }
        
        return { ...item, stock: newStock, status: newStatus, badge: newBadge };
      }
      return item;
    });

    setStockList(updatedList);
    closeModal();
  };

  const filteredStock = stockList.filter(s => {
    if (filter === 'ok') return s.stock > 5;
    if (filter === 'low') return s.stock > 0 && s.stock <= 5;
    if (filter === 'out') return s.stock === 0;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Thanh công cụ lọc */}
      <div className="flex gap-4 justify-end items-center mb-2">
        <select 
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-[#152427] border border-[#24383b] text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-[#0f9d8a] text-sm"
        >
          <option value="all">Tất cả trạng thái</option>
          <option value="ok">Còn hàng</option>
          <option value="low">Sắp hết</option>
          <option value="out">Hết hàng</option>
        </select>
      </div>

      {/* Bảng danh sách Tồn kho */}
      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[620px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-4 font-semibold">Sản phẩm</th>
              <th className="p-4 font-semibold">Màu</th>
              <th className="p-4 font-semibold">Size</th>
              <th className="p-4 font-semibold">Tồn</th>
              <th className="p-4 font-semibold">Trạng thái</th>
              <th className="p-4 font-semibold text-center">Thao tác</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {filteredStock.map((s) => (
              <tr key={s.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 font-bold">{s.name}</td>
                <td className="p-4">{s.color}</td>
                <td className="p-4">{s.size}</td>
                <td className="p-4 font-bold text-lg">{s.stock}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${s.badge}`}>
                    {s.status}
                  </span>
                </td>
                <td className="p-4 text-center">
                  <button 
                    onClick={() => openModal(s)}
                    className="border border-[#24383b] text-[#92a9ad] px-4 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors"
                  >
                    Điều chỉnh
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal Điều Chỉnh Tồn Kho */}
      {modalOpen && selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#152427] border border-[#24383b] rounded-2xl w-full max-w-md p-6 shadow-2xl animate-fade-in-up">
            <h3 className="text-lg font-bold mb-1">Điều chỉnh tồn kho</h3>
            <p className="text-[#92a9ad] text-sm mb-6">
              {selectedItem.name} • {selectedItem.color} / {selectedItem.size} • Tồn hiện tại: <span className="font-bold text-white">{selectedItem.stock}</span>
            </p>

            <form onSubmit={handleAdjustSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Loại điều chỉnh</label>
                <select 
                  value={adjustType} onChange={(e) => setAdjustType(e.target.value)}
                  className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm font-semibold"
                >
                  <option value="1">Nhập thêm (+)</option>
                  <option value="-1">Xuất / hao hụt (−)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Số lượng</label>
                <input 
                  type="number" min="1" required
                  value={adjustQty} onChange={(e) => setAdjustQty(e.target.value)}
                  className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Lý do</label>
                <select 
                  value={adjustReason} onChange={(e) => setAdjustReason(e.target.value)}
                  className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm"
                >
                  {adjustType === '1' ? (
                    <>
                      <option>Nhập hàng mới</option>
                      <option>Hàng trả nhập lại kho</option>
                      <option>Kiểm kê chênh lệch (thừa)</option>
                    </>
                  ) : (
                    <>
                      <option>Hàng lỗi / hư hỏng</option>
                      <option>Kiểm kê chênh lệch (thiếu)</option>
                      <option>Xuất hàng mẫu / tiêu hủy</option>
                    </>
                  )}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-[#24383b] mt-6">
                <button 
                  type="button" 
                  onClick={closeModal}
                  className="px-5 py-2.5 rounded-xl text-sm font-bold border border-[#24383b] text-[#92a9ad] hover:text-white hover:bg-[#24383b] transition-colors"
                >
                  Hủy
                </button>
                <button 
                  type="submit" 
                  className="bg-[#0f9d8a] text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors"
                >
                  Xác nhận
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockAdjustments;