import React, { useState } from 'react';

const initialSizeChart = [
  { id: 1, size: 'S', height: '150–158', weight: '42–50', chest: '80–84', waist: '62–66' },
  { id: 2, size: 'M', height: '158–165', weight: '50–58', chest: '84–88', waist: '66–70' },
  { id: 3, size: 'L', height: '165–172', weight: '58–66', chest: '88–94', waist: '70–76' },
  { id: 4, size: 'XL', height: '172–180', weight: '66–76', chest: '94–100', waist: '76–82' }
];

const SizeChart = () => {
  const [sizes, setSizes] = useState(initialSizeChart);
  const [newSize, setNewSize] = useState({ size: '', height: '', weight: '', chest: '', waist: '' });

  const handleAddSize = (e) => {
    e.preventDefault();
    if (!newSize.size) return;
    setSizes([...sizes, { id: Date.now(), ...newSize }]);
    setNewSize({ size: '', height: '', weight: '', chest: '', waist: '' });
  };

  const handleDelete = (id) => {
    setSizes(sizes.filter(s => s.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Form Thêm thông số Size */}
      <form onSubmit={handleAddSize} className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Size (Ký hiệu)</label>
          <input 
            value={newSize.size} onChange={(e) => setNewSize({...newSize, size: e.target.value})}
            placeholder="VD: XXL" required
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Chiều cao (cm)</label>
          <input 
            value={newSize.height} onChange={(e) => setNewSize({...newSize, height: e.target.value})}
            placeholder="180-185" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Cân nặng (kg)</label>
          <input 
            value={newSize.weight} onChange={(e) => setNewSize({...newSize, weight: e.target.value})}
            placeholder="76-85" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Ngực (cm)</label>
          <input 
            value={newSize.chest} onChange={(e) => setNewSize({...newSize, chest: e.target.value})}
            placeholder="100-106" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <div className="flex-1 min-w-[120px]">
          <label className="block text-xs font-semibold text-[#92a9ad] mb-2">Eo (cm)</label>
          <input 
            value={newSize.waist} onChange={(e) => setNewSize({...newSize, waist: e.target.value})}
            placeholder="82-88" 
            className="w-full bg-[#0e1a1c] border border-[#24383b] text-white px-4 py-2.5 rounded-xl outline-none focus:border-[#0f9d8a] text-sm" 
          />
        </div>
        <button type="submit" className="bg-[#0f9d8a] text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] transition-colors">
          ＋ Thêm
        </button>
      </form>

      {/* Bảng hiển thị thông số */}
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
                <td className="p-4">{s.height}</td>
                <td className="p-4">{s.weight}</td>
                <td className="p-4">{s.chest}</td>
                <td className="p-4">{s.waist}</td>
                <td className="p-4 text-center">
                  <button 
                    onClick={() => handleDelete(s.id)}
                    className="border border-[#24383b] text-[#e5484d] px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#3a1a1e] transition-colors"
                  >
                    Xóa
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

export default SizeChart;