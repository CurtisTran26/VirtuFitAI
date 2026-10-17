import React, { useState } from 'react';
import SizeChart from '../size-charts/SizeChart';

const mockCategories = ['Áo', 'Quần', 'Váy / Đầm', 'Áo khoác'];
const mockColors = [
  { name: 'Trắng', hex: '#ffffff' },
  { name: 'Đen', hex: '#111111' },
  { name: 'Xanh navy', hex: '#1f3a6e' },
  { name: 'Be', hex: '#d9c5a3' },
  { name: 'Đỏ đô', hex: '#8b1e2d' }
];
const mockSizes = ['S', 'M', 'L', 'XL'];

const Catalog = () => {
  const [subTab, setSubTab] = useState('cat');

  return (
    <div className="space-y-4">
      {/* Tabs Menu */}
      <div className="flex gap-2 flex-wrap mb-4">
        {[
          { id: 'cat', label: 'Danh mục' },
          { id: 'col', label: 'Màu sắc' },
          { id: 'siz', label: 'Size' },
          { id: 'chart', label: 'Bảng size' }
        ].map(t => (
          <button 
            key={t.id}
            onClick={() => setSubTab(t.id)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
              subTab === t.id 
                ? 'bg-[#12383a] text-[#0f9d8a] border border-[#0f9d8a]' 
                : 'bg-[#152427] text-[#92a9ad] border border-[#24383b] hover:border-[#0f9d8a]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Nội dung cấu hình */}
      {subTab !== 'chart' ? (
        <div className="bg-[#152427] border border-[#24383b] rounded-2xl p-5">
          <div className="flex gap-4 mb-6">
            <input 
              type="text" 
              placeholder={`Nhập tên ${subTab === 'cat' ? 'danh mục' : subTab === 'col' ? 'màu' : 'size'} mới...`} 
              className="flex-1 bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl focus:outline-none focus:border-[#0f9d8a] text-sm"
            />
            <button className="bg-[#0f9d8a] text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors">
              ＋ Thêm
            </button>
          </div>

          {subTab === 'cat' && (
            <div className="space-y-0">
              {mockCategories.map((c, i) => (
                <div key={i} className="flex justify-between items-center py-3 border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/20 transition-colors">
                  <span className="font-medium text-[#e8f2f1]">{c}</span>
                  <button className="text-[#e5484d] text-xs font-bold hover:underline">Xóa</button>
                </div>
              ))}
            </div>
          )}

          {subTab === 'col' && (
            <div className="space-y-0">
              {mockColors.map((c, i) => (
                <div key={i} className="flex justify-between items-center py-3 border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="w-4 h-4 rounded-full border border-[#24383b]" style={{ backgroundColor: c.hex }}></span>
                    <span className="font-medium text-[#e8f2f1]">{c.name}</span>
                    <span className="text-[#92a9ad] text-xs">{c.hex}</span>
                  </div>
                  <button className="text-[#e5484d] text-xs font-bold hover:underline">Xóa</button>
                </div>
              ))}
            </div>
          )}

          {subTab === 'siz' && (
            <div className="flex flex-wrap gap-3">
              {mockSizes.map((s, i) => (
                <div key={i} className="bg-[#12383a] text-[#0f9d8a] px-4 py-2 rounded-xl flex items-center gap-3 font-bold hover:bg-[#0f9d8a] hover:text-white transition-colors">
                  {s}
                  <button className="text-current hover:text-[#e5484d] transition-colors ml-1">✕</button>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Gọi giao diện Component Bảng size vào đây */
        <SizeChart />
      )}
    </div>
  );
};

export default Catalog;