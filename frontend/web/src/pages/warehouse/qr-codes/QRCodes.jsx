import React, { useState, useRef } from 'react';

const mockProducts = [
  { id: 1, name: 'Áo sơ mi linen', sku: 'VF-AS-001' },
  { id: 2, name: 'Đầm midi hoa', sku: 'VF-DM-014' },
  { id: 3, name: 'Quần jeans slim', sku: 'VF-QJ-007' },
  { id: 4, name: 'Áo khoác bomber', sku: 'VF-AK-003' },
  { id: 5, name: 'Váy xếp ly', sku: 'VF-VX-009' }
];

// Hàm tạo mã SVG QR Code giả lập dựa trên thuật toán hash của SKU
const generateQRCodeSVG = (seed) => {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const n = 21;
  const rects = [];
  
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      if ((x < 8 && y < 8) || (x > 12 && y < 8) || (x < 8 && y > 12)) continue;
      h = (h * 1103515245 + 12345) >>> 0;
      if ((h >> 16) & 1) {
        rects.push(<rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill="#000" />);
      }
    }
  }

  const Finder = ({ x, y }) => (
    <g>
      <rect x={x} y={y} width="7" height="7" fill="#000" />
      <rect x={x + 1} y={y + 1} width="5" height="5" fill="#fff" />
      <rect x={x + 2} y={y + 2} width="3" height="3" fill="#000" />
    </g>
  );

  return (
    <svg viewBox="-1 -1 23 23" xmlns="http://www.w3.org/2000/svg" shapeRendering="crispEdges" className="w-[130px] h-[130px] bg-white p-1.5 rounded-lg border border-[#24383b]">
      {rects}
      <Finder x={0} y={0} />
      <Finder x={14} y={0} />
      <Finder x={0} y={14} />
    </svg>
  );
};

const QRCodes = () => {
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [generatedQRs, setGeneratedQRs] = useState([]);
  const previewRef = useRef(null);

  const toggleSelect = (id) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedIds(newSet);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === mockProducts.length) {
      setSelectedIds(new Set()); // Bỏ chọn tất cả nếu đang chọn full
    } else {
      setSelectedIds(new Set(mockProducts.map(p => p.id))); // Chọn tất cả
    }
  };

  const handleGenerate = () => {
    if (selectedIds.size === 0) {
      alert('Vui lòng chọn ít nhất 1 sản phẩm!');
      return;
    }
    const qrsToGenerate = mockProducts.filter(p => selectedIds.has(p.id));
    setGeneratedQRs(qrsToGenerate);
  };

  const handleDownload = () => {
    if (generatedQRs.length === 0) {
      alert('Hãy tạo mã QR trước khi tải xuống!');
      return;
    }
    
    // Logic tải SVG (mô phỏng tải file gộp hoặc từng file)
    const svgElements = previewRef.current.querySelectorAll('svg');
    if (svgElements.length > 0) {
      const svgData = new XMLSerializer().serializeToString(svgElements[0]);
      const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `QR-${generatedQRs[0].sku}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="space-y-4">
      {/* Thanh công cụ */}
      <div className="flex gap-3 justify-end items-center mb-4 flex-wrap">
        <button 
          onClick={handleSelectAll}
          className="bg-[#152427] border border-[#24383b] text-[#92a9ad] px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#24383b] hover:text-white transition-colors"
        >
          {selectedIds.size === mockProducts.length ? 'Bỏ chọn tất cả' : 'Chọn tất cả'}
        </button>
        <button 
          onClick={handleGenerate}
          className="bg-[#0f9d8a] text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-[#0b7a6c] shadow-lg transition-colors"
        >
          Tạo mã QR đã chọn
        </button>
        <button 
          onClick={handleDownload}
          className="bg-[#152427] border border-[#24383b] text-white px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#24383b] transition-colors"
        >
          ⬇ Tải xuống
        </button>
      </div>

      {/* Bảng chọn Sản phẩm */}
      <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto mb-4">
        <table className="w-full text-left min-w-[500px]">
          <thead>
            <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
              <th className="p-4 w-12 text-center"></th>
              <th className="p-4 font-semibold">Sản phẩm</th>
              <th className="p-4 font-semibold">SKU</th>
              <th className="p-4 font-semibold">Mã QR</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {mockProducts.map((p) => (
              <tr key={p.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                <td className="p-4 text-center">
                  <input 
                    type="checkbox" 
                    checked={selectedIds.has(p.id)}
                    onChange={() => toggleSelect(p.id)}
                    className="w-4 h-4 accent-[#0f9d8a] cursor-pointer"
                  />
                </td>
                <td className="p-4 font-bold text-white">{p.name}</td>
                <td className="p-4 text-[#92a9ad]">{p.sku}</td>
                <td className="p-4">
                  <span className="bg-[#17284a] text-[#3b82f6] px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap">
                    QR-{p.sku}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Khu vực Xem trước QR Code */}
      <div className="bg-[#152427] border border-[#24383b] rounded-2xl p-6">
        <h3 className="text-lg font-bold mb-4">Xem trước</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" ref={previewRef}>
          {generatedQRs.length === 0 ? (
            <p className="text-[#92a9ad] col-span-full">Chọn sản phẩm ở trên rồi bấm “Tạo mã QR”.</p>
          ) : (
            generatedQRs.map((p) => (
              <div key={p.id} className="flex flex-col items-center justify-center p-4 border border-[#24383b] rounded-xl text-center bg-[#0e1a1c]">
                {generateQRCodeSVG(p.sku)}
                <p className="mt-3 font-bold text-sm text-white">{p.name}</p>
                <p className="text-xs text-[#92a9ad] mt-1">{p.sku}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default QRCodes;