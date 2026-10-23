import React, { useState } from 'react';

const initialSizeChart = [
  { id: 1, size: 'S', height: '150–158', weight: '42–50', chest: '80–84', waist: '62–66' },
  { id: 2, size: 'M', height: '158–165', weight: '50–58', chest: '84–88', waist: '66–70' },
  { id: 3, size: 'L', height: '165–172', weight: '58–66', chest: '88–94', waist: '70–76' },
  { id: 4, size: 'XL', height: '172–180', weight: '66–76', chest: '94–100', waist: '76–82' }
];

const SizeChart = () => {
  const [sizes, setSizes] = useState(initialSizeChart);
  
  // Dùng chung state cho cả Thêm mới và Sửa
  const [formData, setFormData] = useState({ size: '', height: '', weight: '', chest: '', waist: '' });
  const [editingId, setEditingId] = useState(null);

  // XỬ LÝ LƯU (Gộp chung Thêm và Sửa)
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.size) return;

    if (editingId) {
      // Logic Cập nhật (Sửa)
      setSizes(sizes.map(s => s.id === editingId ? { ...formData, id: editingId } : s));
      setEditingId(null);
    } else {
      // Logic Thêm mới
      setSizes([...sizes, { id: Date.now(), ...formData }]);
    }
    
    // Xóa trắng form sau khi lưu
    setFormData({ size: '', height: '', weight: '', chest: '', waist: '' });
  };

  // MỞ CHẾ ĐỘ SỬA
  const handleEdit = (item) => {
    setEditingId(item.id);
    setFormData({ 
      size: item.size, 
      height: item.height, 
      weight: item.weight, 
      chest: item.chest, 
      waist: item.waist 
    });
  };

  // HỦY SỬA
  const handleCancel = () => {
    setEditingId(null);
    setFormData({ size: '', height: '', weight: '', chest: '', waist: '' });
  };

  // XÓA
  const handleDelete = (id, sizeName) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa thông số size "${sizeName}" không?`)) {
      setSizes(sizes.filter(s => s.id !== id));
      // Nếu đang sửa chính nó mà bấm xóa thì reset form
      if (editingId === id) handleCancel();
    }
  };

  return (
    <div className="space-y-6">
      {/* FORM NHẬP LIỆU (THÊM / SỬA) */}
      <form onSubmit={handleSubmit} className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl flex flex-wrap gap-4 items-end transition-all">
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Size (Ký hiệu)</label>
          <input 
            value={formData.size} onChange={(e) => setFormData({...formData, size: e.target.value})}
            placeholder="VD: XXL" required
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Chiều cao (cm)</label>
          <input 
            value={formData.height} onChange={(e) => setFormData({...formData, height: e.target.value})}
            placeholder="180-185" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Cân nặng (kg)</label>
          <input 
            value={formData.weight} onChange={(e) => setFormData({...formData, weight: e.target.value})}
            placeholder="76-85" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Ngực (cm)</label>
          <input 
            value={formData.chest} onChange={(e) => setFormData({...formData, chest: e.target.value})}
            placeholder="100-106" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Eo (cm)</label>
          <input 
            value={formData.waist} onChange={(e) => setFormData({...formData, waist: e.target.value})}
            placeholder="82-88" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        
        {/* Nút thao tác Form */}
        <div className="flex gap-2">
          {editingId && (
            <button type="button" onClick={handleCancel} className="bg-transparent border border-[#24383b] text-[#92a9ad] px-4 py-2.5 rounded-xl text-sm font-bold hover:text-white hover:bg-[#24383b] transition-colors">
              Hủy
            </button>
          )}
          <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors">
            {editingId ? 'Cập nhật' : '＋ Thêm'}
          </button>
        </div>
      </form>

      {/* BẢNG HIỂN THỊ THÔNG SỐ */}
      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[620px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-4 font-semibold">Size</th>
              <th className="p-4 font-semibold">Chiều cao (cm)</th>
              <th className="p-4 font-semibold">Cân nặng (kg)</th>
              <th className="p-4 font-semibold">Ngực (cm)</th>
              <th className="p-4 font-semibold">Eo (cm)</th>
              <th className="p-4 font-semibold text-center">Thao tác</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {sizes.map((s) => (
              <tr key={s.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 font-bold text-[#0f9d8a] text-lg">{s.size}</td>
                <td className="p-4 text-white">{s.height}</td>
                <td className="p-4 text-white">{s.weight}</td>
                <td className="p-4 text-white">{s.chest}</td>
                <td className="p-4 text-white">{s.waist}</td>
                <td className="p-4">
                  <div className="flex gap-2 justify-center">
                    <button 
                      onClick={() => handleEdit(s)}
                      className="border border-[#24383b] text-[#92a9ad] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors"
                    >
                      Sửa
                    </button>
                    <button 
                      onClick={() => handleDelete(s.id, s.size)}
                      className="border border-[#3a1a1e] text-[#e5484d] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#3a1a1e] transition-colors"
                    >
                      Xóa
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            
            {sizes.length === 0 && (
              <tr>
                <td colSpan="6" className="p-8 text-center text-[#92a9ad] text-sm">
                  Chưa có thông số bảng size nào. Hãy thêm mới ở trên.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SizeChart;