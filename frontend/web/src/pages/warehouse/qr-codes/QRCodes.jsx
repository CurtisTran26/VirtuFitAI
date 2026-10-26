import React, { useCallback, useEffect, useMemo, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const QRCodes = () => {
  const [products, setProducts] = useState([]);
  const [query, setQuery] = useState('');
  const [busyId, setBusyId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [previewProduct, setPreviewProduct] = useState(null);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiClient.get('products?page=1&limit=100');
      setProducts(result.items || []);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadProducts(); }, [loadProducts]);

  const generateQR = async (product) => {
    setBusyId(product.id);
    setError('');
    try {
      const qr = await apiClient.post(`admin/products/${product.id}/qr`, {});
      setProducts((current) => current.map((item) => item.id === product.id ? { ...item, qr_data: qr.qr_data, qr_image_url: qr.qr_image_url } : item));
    } catch (generateError) {
      setError(generateError.message);
    } finally {
      setBusyId(null);
    }
  };

  const visibleProducts = useMemo(() => products.filter((product) => `${product.name} ${product.sku} ${product.category_name}`.toLowerCase().includes(query.trim().toLowerCase())), [products, query]);

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
        <h1 className="font-bold">Mã QR sản phẩm</h1>
        <p className="mt-1 text-sm text-[#92a9ad]">Tạo hoặc cấp mới mã QR cho sản phẩm. Mã QR lưu deep link theo UUID của sản phẩm hiện tại.</p>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <input className="w-full max-w-sm rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none focus:border-[#0f9d8a]" placeholder="Tìm tên / SKU sản phẩm" value={query} onChange={(event) => setQuery(event.target.value)} />
        <button type="button" className="text-sm text-[#0f9d8a] disabled:opacity-50" onClick={loadProducts} disabled={loading}>Tải lại</button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Sản phẩm</th><th className="p-3">SKU</th><th className="p-3">Danh mục</th><th className="p-3">Mã QR</th><th className="p-3 text-right">Thao tác</th></tr></thead>
          <tbody>
            {!loading && visibleProducts.map((product) => <tr key={product.id} className="border-b border-[#24383b] last:border-0">
              <td className="p-3 font-semibold">{product.name}</td>
              <td className="p-3">{product.sku}</td>
              <td className="p-3">{product.category_name}</td>
              <td className="p-3">{product.qr_image_url ? <div className="flex items-center gap-3"><button type="button" onClick={() => setPreviewProduct(product)} title="Xem mã QR cỡ lớn" className="rounded-lg bg-white p-1"><img src={product.qr_image_url} alt={`QR ${product.name}`} className="h-24 w-24 rounded object-contain" /></button><a href={product.qr_image_url} download={`QR-${product.sku}.png`} target="_blank" rel="noreferrer" className="text-sm font-semibold text-[#48c6b2]">Tải ảnh QR</a></div> : <span className="text-sm text-[#92a9ad]">Chưa tạo</span>}</td>
              <td className="p-3 text-right"><button type="button" disabled={!product.is_active || busyId === product.id} onClick={() => generateQR(product)} className="rounded-lg bg-[#0f9d8a] px-3 py-1.5 text-xs font-bold text-white disabled:cursor-not-allowed disabled:opacity-50">{busyId === product.id ? 'Đang tạo…' : product.qr_image_url ? 'Cấp mới mã QR' : 'Tạo mã QR'}</button></td>
            </tr>)}
            {!loading && visibleProducts.length === 0 && <tr><td colSpan="5" className="p-8 text-center text-[#92a9ad]">{products.length ? 'Không tìm thấy sản phẩm.' : 'Chưa có sản phẩm trong backend.'}</td></tr>}
            {loading && <tr><td colSpan="5" className="p-8 text-center text-[#92a9ad]">Đang tải sản phẩm…</td></tr>}
          </tbody>
        </table>
      </div>

      {previewProduct && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) setPreviewProduct(null); }}>
        <section role="dialog" aria-modal="true" aria-labelledby="qr-preview-title" className="w-full max-w-md rounded-2xl border border-[#24383b] bg-[#152427] p-5 text-center shadow-2xl">
          <h2 id="qr-preview-title" className="font-bold">Mã QR · {previewProduct.name}</h2>
          <p className="mt-1 text-sm text-[#92a9ad]">SKU: {previewProduct.sku}</p>
          <img src={previewProduct.qr_image_url} alt={`Mã QR sản phẩm ${previewProduct.name}`} className="mx-auto mt-4 h-80 w-80 max-w-full rounded-xl bg-white p-3 object-contain" />
          <p className="mt-3 break-all rounded-lg bg-[#0e1a1c] p-3 text-xs text-[#92a9ad]">{previewProduct.qr_data}</p>
          <div className="mt-4 flex justify-center gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2 text-sm" onClick={() => setPreviewProduct(null)}>Đóng</button><a href={previewProduct.qr_image_url} download={`QR-${previewProduct.sku}.png`} target="_blank" rel="noreferrer" className="rounded-lg bg-[#0f9d8a] px-4 py-2 text-sm font-bold text-white">Tải ảnh QR</a></div>
        </section>
      </div>}
    </div>
  );
};

export default QRCodes;
