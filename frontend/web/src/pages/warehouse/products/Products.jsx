import React, { useState } from 'react';

// Dữ liệu mẫu ban đầu
const initialProducts = [
  { id: 1, name: 'Áo sơ mi linen', sku: 'VF-AS-001', cat: 'Áo', price: 459000, stock: 28, active: true, icon: '👔' },
  { id: 2, name: 'Đầm midi hoa', sku: 'VF-DM-014', cat: 'Váy / Đầm', price: 689000, stock: 12, active: true, icon: '👗' },
  { id: 3, name: 'Quần jeans slim', sku: 'VF-QJ-007', cat: 'Quần', price: 539000, stock: 5, active: true, icon: '👖' },
  { id: 4, name: 'Áo khoác bomber', sku: 'VF-AK-003', cat: 'Áo khoác', price: 799000, stock: 21, active: true, icon: '🧥' },
  { id: 5, name: 'Váy xếp ly', sku: 'VF-VX-009', cat: 'Váy / Đầm', price: 419000, stock: 0, active: false, icon: '👗' }
];

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + '₫';

const Products = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [productList, setProductList] = useState(initialProducts);
  
  // Các state quản lý Form
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    cat: 'Áo',
    price: '',
    stock: 0,
    active: true
  });

  const handleOpenAdd = () => {
    setEditingId(null);
    setFormData({ name: '', sku: '', cat: 'Áo', price: '', stock: 0, active: true });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      sku: product.sku,
      cat: product.cat,
      price: product.price,
      stock: product.stock,
      active: product.active
    });
    setIsModalOpen(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (editingId) {
      const updatedList = productList.map(p => 
        p.id === editingId ? { ...p, ...formData, price: Number(formData.price), stock: Number(formData.stock) } : p
      );
      setProductList(updatedList);
    } else {
      const newProduct = {
        id: Date.now(),
        ...formData,
        price: Number(formData.price),
        stock: Number(formData.stock),
        icon: '📦'
      };
      setProductList([newProduct, ...productList]);
    }
    setIsModalOpen(false);
  };

  const handleToggleStatus = (id) => {
    const updatedList = productList.map(p => 
      p.id === id ? { ...p, active: !p.active } : p
    );
    setProductList(updatedList);
  };

  const filteredProducts = productList.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4 relative">
      <div className="flex flex-wrap gap-4 justify-between items-center mb-2">
        <input 
          type="text" 
          placeholder="🔍 Tìm tên / SKU" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-[#152427] border border-[#24383b] text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-[#0f9d8a] min-w-[260px] text-sm" 
        />
        <button 
          onClick={handleOpenAdd}
          className="bg-[#0f9d8a] text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] shadow-lg transition-colors"
        >
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
              <th className="p-4">Thao tác</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {filteredProducts.map((p) => (
              <tr key={p.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 font-bold flex items-center gap-3 text-white">
                  <div className="w-10 h-10 rounded-xl bg-[#12383a] flex items-center justify-center text-xl">{p.icon}</div>
                  {p.name}
                </td>
                <td className="p-4 text-[#92a9ad]">{p.sku}</td>
                <td className="p-4 text-[#92a9ad]">{p.cat}</td>
                <td className="p-4 text-white font-medium">{formatPrice(p.price)}</td>
                <td className="p-4 text-white font-bold">{p.stock}</td>
                <td className="p-4">
                  <button 
                    onClick={() => handleToggleStatus(p.id)}
                    className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-colors ${p.active ? 'bg-[#0f2e24] text-[#12a66a] hover:bg-[#0f2e24]/70' : 'bg-[#3a1a1e] text-[#e5484d] hover:bg-[#3a1a1e]/70'}`}
                  >
                    {p.active ? 'Đang bán' : 'Ngừng bán'}
                  </button>
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => handleOpenEdit(p)}
                    className="border border-[#24383b] text-[#92a9ad] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#24383b] hover:text-white transition-colors"
                  >
                    Sửa
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL FORM: Giao diện mới */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-fade-in overflow-y-auto py-10">
          <div className="bg-[#152427] border border-[#24383b] p-6 rounded-2xl w-full max-w-3xl shadow-2xl my-auto">
            <h2 className="text-white text-lg font-bold mb-6">
              {editingId ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="flex gap-6">
                <div className="flex-1">
                  <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Tên sản phẩm</label>
                  <input required type="text" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors"
                    value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                </div>
                <div className="flex-1">
                  <label className="text-[#92a9ad] text-xs font-semibold block mb-2">SKU</label>
                  <input required type="text" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors"
                    value={formData.sku} onChange={e => setFormData({...formData, sku: e.target.value})} />
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-1/3">
                  <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Danh mục</label>
                  <select className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors appearance-none"
                    value={formData.cat} onChange={e => setFormData({...formData, cat: e.target.value})}>
                    <option value="Áo">Áo</option>
                    <option value="Quần">Quần</option>
                    <option value="Váy / Đầm">Váy / Đầm</option>
                    <option value="Áo khoác">Áo khoác</option>
                  </select>
                </div>
                <div className="w-1/3">
                  <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Giá bán (₫)</label>
                  <input required type="number" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors"
                    value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} />
                </div>
                <div className="w-1/3">
                  <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Tồn kho</label>
                  <input required type="number" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors"
                    value={formData.stock} onChange={e => setFormData({...formData, stock: e.target.value})} />
                </div>
              </div>

              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-3">Màu sắc</label>
                <div className="flex flex-wrap gap-x-8 gap-y-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                    <span className="w-3 h-3 rounded-full bg-white border border-gray-300"></span>
                    <span className="text-white text-sm">Trắng</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                    <span className="w-3 h-3 rounded-full bg-black border border-gray-600"></span>
                    <span className="text-white text-sm">Đen</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                    <span className="w-3 h-3 rounded-full bg-blue-900 border border-blue-900"></span>
                    <span className="text-white text-sm">Xanh navy</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                    <span className="w-3 h-3 rounded-full bg-[#f5f5dc] border border-gray-300"></span>
                    <span className="text-white text-sm">Be</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                    <span className="w-3 h-3 rounded-full bg-[#800000] border border-[#800000]"></span>
                    <span className="text-white text-sm">Đỏ đô</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-3">Size</label>
                <div className="flex gap-8">
                  {['S', 'M', 'L', 'XL'].map((size) => (
                    <label key={size} className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 rounded border-[#24383b] bg-[#0a1516] text-[#0f9d8a] focus:ring-0 cursor-pointer accent-[#0f9d8a]" defaultChecked />
                      <span className="text-white text-sm font-bold">{size}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Mô tả</label>
                <textarea rows="3" className="w-full bg-[#0a1516] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:border-[#0f9d8a] transition-colors resize-none"></textarea>
              </div>
              
              <div>
                <label className="text-[#92a9ad] text-xs font-semibold block mb-2">Hình ảnh</label>
                <div className="w-full bg-[#0a1516] border border-[#24383b] text-[#92a9ad] px-4 py-3 rounded-xl text-sm focus:outline-none flex items-center justify-center border-dashed cursor-pointer hover:border-[#0f9d8a] transition-colors">
                  <span>+ Kéo thả hoặc click để chọn ảnh</span>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setIsModalOpen(false)} className="border border-[#24383b] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#24383b] transition-colors">
                  Hủy
                </button>
                <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors shadow-lg">
                  {editingId ? 'Cập nhật' : 'Lưu sản phẩm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;