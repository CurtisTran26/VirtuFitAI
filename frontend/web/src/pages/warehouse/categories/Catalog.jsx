import React, { useState } from 'react';

// ==========================================
// 1. COMPONENT DÙNG CHUNG (Cho Danh mục, Màu sắc, Size)
// ==========================================
const SubAttributeManager = ({ title, placeholder, list, setList }) => {
  const [inputValue, setInputValue] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    const val = inputValue.trim();
    if (val && !list.includes(val)) {
      setList([...list, val]);
      setInputValue('');
    }
  };

  const handleDelete = (item) => {
    if (window.confirm(`Bạn có chắc muốn xóa ${title.toLowerCase()} "${item}"?`)) {
      setList(list.filter((i) => i !== item));
    }
  };

  return (
    <div className="bg-[#152427] border border-[#24383b] rounded-2xl w-full max-w-4xl p-6">
      <form onSubmit={handleAdd} className="flex gap-4 mb-2">
        <input
          type="text"
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="flex-1 bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a]"
        />
        <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors whitespace-nowrap">
          + Thêm
        </button>
      </form>
      <div className="flex flex-col">
        {list.map((item, index) => (
          <div key={index} className="flex justify-between items-center py-4 border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors px-2 rounded-lg -mx-2">
            <span className="text-white text-sm font-bold">{item}</span>
            <button onClick={() => handleDelete(item)} className="text-[#e5484d] text-xs font-bold hover:text-red-400 transition-colors">Xóa</button>
          </div>
        ))}
        {list.length === 0 && <div className="py-6 text-[#92a9ad] text-sm text-center">Chưa có {title.toLowerCase()} nào.</div>}
      </div>
    </div>
  );
};

// ==========================================
// 2. COMPONENT BẢNG SIZE (Kèm tính năng Sửa/Xóa/Thêm)
// ==========================================
const initialSizeChart = [
  { id: 1, size: 'S', height: '150–158', weight: '42–50', chest: '80–84', waist: '62–66' },
  { id: 2, size: 'M', height: '158–165', weight: '50–58', chest: '84–88', waist: '66–70' },
  { id: 3, size: 'L', height: '165–172', weight: '58–66', chest: '88–94', waist: '70–76' },
  { id: 4, size: 'XL', height: '172–180', weight: '66–76', chest: '94–100', waist: '76–82' }
];

const SizeChartTab = () => {
  const [sizes, setSizes] = useState(initialSizeChart);
  const [formData, setFormData] = useState({ size: '', height: '', weight: '', chest: '', waist: '' });
  const [editingId, setEditingId] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.size) return;
    if (editingId) {
      setSizes(sizes.map(s => s.id === editingId ? { ...formData, id: editingId } : s));
      setEditingId(null);
    } else {
      setSizes([...sizes, { id: Date.now(), ...formData }]);
    }
    setFormData({ size: '', height: '', weight: '', chest: '', waist: '' });
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setFormData({ size: item.size, height: item.height, weight: item.weight, chest: item.chest, waist: item.waist });
  };

  const handleCancel = () => {
    setEditingId(null);
    setFormData({ size: '', height: '', weight: '', chest: '', waist: '' });
  };

  const handleDelete = (id, sizeName) => {
    if (window.confirm(`Xóa thông số size "${sizeName}"?`)) {
      setSizes(sizes.filter(s => s.id !== id));
      if (editingId === id) handleCancel();
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[120px]"><label className="block text-xs font-semibold text-[#92a9ad] mb-2">Size</label><input required value={formData.size} onChange={(e) => setFormData({...formData, size: e.target.value})} placeholder="VD: XXL" className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" /></div>
        <div className="flex-1 min-w-[120px]"><label className="block text-xs font-semibold text-[#92a9ad] mb-2">Chiều cao</label><input value={formData.height} onChange={(e) => setFormData({...formData, height: e.target.value})} placeholder="180-185" className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" /></div>
        <div className="flex-1 min-w-[120px]"><label className="block text-xs font-semibold text-[#92a9ad] mb-2">Cân nặng</label><input value={formData.weight} onChange={(e) => setFormData({...formData, weight: e.target.value})} placeholder="76-85" className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" /></div>
        <div className="flex-1 min-w-[120px]"><label className="block text-xs font-semibold text-[#92a9ad] mb-2">Ngực</label><input value={formData.chest} onChange={(e) => setFormData({...formData, chest: e.target.value})} placeholder="100-106" className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" /></div>
        <div className="flex-1 min-w-[120px]"><label className="block text-xs font-semibold text-[#92a9ad] mb-2">Eo</label><input value={formData.waist} onChange={(e) => setFormData({...formData, waist: e.target.value})} placeholder="82-88" className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" /></div>
        <div className="flex gap-2">
          {editingId && <button type="button" onClick={handleCancel} className="bg-transparent border border-[#24383b] text-[#92a9ad] px-4 py-2.5 rounded-xl text-sm font-bold hover:text-white hover:bg-[#24383b] transition-colors">Hủy</button>}
          <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors">{editingId ? 'Cập nhật' : '＋ Thêm'}</button>
        </div>
      </form>
      
      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
        <table className="w-full text-left min-w-[620px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-4 font-semibold">Size</th><th className="p-4 font-semibold">Chiều cao (cm)</th><th className="p-4 font-semibold">Cân nặng (kg)</th><th className="p-4 font-semibold">Ngực (cm)</th><th className="p-4 font-semibold">Eo (cm)</th><th className="p-4 font-semibold text-center">Thao tác</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {sizes.map((s) => (
              <tr key={s.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 font-bold text-[#0f9d8a] text-lg">{s.size}</td><td className="p-4 text-white">{s.height}</td><td className="p-4 text-white">{s.weight}</td><td className="p-4 text-white">{s.chest}</td><td className="p-4 text-white">{s.waist}</td>
                <td className="p-4">
                  <div className="flex gap-2 justify-center">
                    <button onClick={() => handleEdit(s)} className="border border-[#24383b] text-[#92a9ad] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors">Sửa</button>
                    <button onClick={() => handleDelete(s.id, s.size)} className="border border-[#3a1a1e] text-[#e5484d] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#3a1a1e] transition-colors">Xóa</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ==========================================
// 3. FILE CHÍNH (GỘP CÁC TAB)
// ==========================================
const Catalog = () => {
  const [activeTab, setActiveTab] = useState('Danh mục');
  
  // Dữ liệu mẫu khởi tạo
  const [categories, setCategories] = useState(['Áo', 'Quần', 'Váy / Đầm', 'Áo khoác']);
  const [colors, setColors] = useState(['Đen', 'Trắng', 'Be', 'Xanh Navy']);
  const [sizes, setSizes] = useState(['S', 'M', 'L', 'XL', 'XXL']);

  // Đã thêm Bảng size lại vào đây
  const tabs = ['Danh mục', 'Màu sắc', 'Size', 'Bảng size'];

  return (
    <div className="space-y-6">
      {/* THANH TAB ĐIỀU HƯỚNG */}
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2 rounded-xl text-sm font-medium transition-colors border ${
              activeTab === tab
                ? 'border-[#0f9d8a] text-[#0f9d8a] bg-[#0f9d8a]/10'
                : 'border-[#24383b] text-[#92a9ad] hover:border-[#0f9d8a]/50 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* RENDER NỘI DUNG TƯƠNG ỨNG VỚI TAB */}
      {activeTab === 'Danh mục' && <SubAttributeManager title="Danh mục" placeholder="Nhập tên danh mục mới..." list={categories} setList={setCategories} />}
      {activeTab === 'Màu sắc' && <SubAttributeManager title="Màu sắc" placeholder="Nhập tên màu sắc mới..." list={colors} setList={setColors} />}
      {activeTab === 'Size' && <SubAttributeManager title="Size" placeholder="Nhập ký hiệu size mới..." list={sizes} setList={setSizes} />}
      {activeTab === 'Bảng size' && <SizeChartTab />}
    </div>
  );
};

export default Catalog;