import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const inputClass = 'w-full rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none focus:border-[#0f9d8a]';
const emptyForm = { name: '', sku: '', category_id: '', price_vnd: '', description: '', image_url: '', is_active: true, selected_colors: [], selected_sizes: [] };
const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price || 0) + '₫';
const makeVariantSku = (productSku, color, size) => {
  const slug = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[đĐ]/g, (letter) => letter === 'Đ' ? 'D' : 'd').replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').toUpperCase();
  const suffix = `${slug(color)}-${slug(size)}`;
  return `${productSku.slice(0, Math.max(1, 79 - suffix.length))}-${suffix}`;
};

const Products = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [catalogOptions, setCatalogOptions] = useState({ colors: [], sizes: [] });
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [updatingProductIds, setUpdatingProductIds] = useState(() => new Set());
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [isProductModalOpen, setProductModalOpen] = useState(false);
  const [variantProduct, setVariantProduct] = useState(null);
  const [variantForm, setVariantForm] = useState({ size: '', color: '', sku: '' });

  const loadData = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [productResult, categoryResult, optionResult] = await Promise.all([
        apiClient.get('products?page=1&limit=100'),
        apiClient.get('categories?page=1&limit=100'),
        apiClient.get('catalog-options'),
      ]);
      setProducts(productResult.items || []);
      setCategories(categoryResult.items || []);
      setCatalogOptions({ colors: optionResult.colors || [], sizes: optionResult.sizes || [] });
    } catch (loadError) { setError(loadError.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const openForm = async (product = null) => {
    setError('');
    setProductModalOpen(true);
    const formFromProduct = (current) => ({
      name: current.name,
      sku: current.sku,
      category_id: current.category_id,
      price_vnd: current.price_vnd,
      description: current.description || '',
      image_url: current.image_url || '',
      is_active: current.is_active,
      selected_colors: [...new Set((current.variants || []).map((variant) => variant.color).filter(Boolean))],
      selected_sizes: [...new Set((current.variants || []).map((variant) => variant.size).filter(Boolean))],
    });

    if (product) {
      // Open the editor from the list data immediately. The detail request only
      // fills in variants; a failed detail request should not block product edits.
      setEditing({ ...product, variants: [] });
      setForm(formFromProduct(product));
    }
    try {
      const current = product ? await apiClient.get(`products/${product.id}`) : null;
      setEditing(current);
      setForm(current ? formFromProduct(current) : { ...emptyForm, category_id: categories.find((c) => c.is_active)?.id || '' });
    } catch (loadError) {
      // Keep the editor usable with list data if the optional detail request fails.
      setError(`Không tải được biến thể của sản phẩm: ${loadError.message}. Bạn vẫn có thể sửa thông tin sản phẩm.`);
    }
  };

  const submitProduct = async (event) => {
    event.preventDefault(); setError('');
    try {
      const body = {
        category_id: form.category_id,
        name: form.name.trim(),
        sku: form.sku.trim(),
        price_vnd: Number(form.price_vnd),
        description: form.description.trim(),
        image_url: form.image_url.trim() || null,
        is_active: form.is_active,
      };
      const savedProduct = editing
        ? await apiClient.patch(`products/${editing.id}`, body)
        : await apiClient.post('products', body);
      const productId = savedProduct.id || editing.id;
      const selectedPairs = new Set(form.selected_colors.flatMap((color) => form.selected_sizes.map((size) => `${color}\u0000${size}`)));
      const existingVariants = editing?.variants || [];
      const removedVariants = existingVariants.filter((variant) => !selectedPairs.has(`${variant.color}\u0000${variant.size}`));
      for (const variant of removedVariants) {
        try {
          await apiClient.delete(`products/${productId}/variants/${variant.id}`);
        } catch (variantError) {
          await loadData();
          const latestProduct = await apiClient.get(`products/${productId}`);
          setEditing(latestProduct);
          setError(`Không thể xóa biến thể ${variant.color}/${variant.size}: ${variantError.message}`);
          return;
        }
      }
      const existingPairs = new Set(existingVariants
        .filter((variant) => selectedPairs.has(`${variant.color}\u0000${variant.size}`))
        .map((variant) => `${variant.color}\u0000${variant.size}`));
      const variantErrors = [];
      for (const color of form.selected_colors) {
        for (const size of form.selected_sizes) {
          if (existingPairs.has(`${color}\u0000${size}`)) continue;
          try {
            await apiClient.post(`products/${productId}/variants`, {
              product_id: productId,
              color,
              size,
              sku: makeVariantSku(body.sku, color, size),
            });
          } catch (variantError) {
            variantErrors.push(`${color}/${size}: ${variantError.message}`);
          }
        }
      }
      setEditing(null); setProductModalOpen(false); setForm(emptyForm);
      await loadData();
      if (variantErrors.length) setError(`Sản phẩm đã lưu, nhưng một số biến thể chưa tạo được: ${variantErrors.join('; ')}`);
    } catch (submitError) { setError(submitError.message); }
  };

  const toggleSelection = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: current[field].includes(value)
        ? current[field].filter((item) => item !== value)
        : [...current[field], value],
    }));
  };

  const toggleProductStatus = async (product) => {
    const nextActive = !product.is_active;
    setUpdatingProductIds((current) => new Set(current).add(product.id));
    setError('');
    try {
      await apiClient.patch(`products/${product.id}`, {
        category_id: product.category_id,
        name: product.name,
        description: product.description || '',
        price_vnd: product.price_vnd,
        sku: product.sku,
        image_url: product.image_url || null,
        is_active: nextActive,
      });
      await loadData();
    } catch (statusError) { setError(statusError.message); }
    finally {
      setUpdatingProductIds((current) => {
        const next = new Set(current);
        next.delete(product.id);
        return next;
      });
    }
  };

  const submitVariant = async (event) => {
    event.preventDefault(); setError('');
    try {
      await apiClient.post(`products/${variantProduct.id}/variants`, { product_id: variantProduct.id, ...variantForm, size: variantForm.size, color: variantForm.color, sku: variantForm.sku.trim() });
      setVariantProduct(null); setVariantForm({ size: '', color: '', sku: '' }); await loadData();
    } catch (submitError) { setError(submitError.message); }
  };

  const visibleProducts = products.filter((product) => `${product.name} ${product.sku}`.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-[#24383b] bg-[#152427] p-4 text-sm text-[#c5d2d2]">
        <p className="font-semibold text-white">Quy trình sản phẩm</p>
        <p className="mt-1 text-xs leading-5 text-[#92a9ad]">Chọn danh mục, màu sắc và size khi tạo sản phẩm. Hệ thống tạo biến thể theo từng tổ hợp màu/size; tồn kho được quản lý riêng ở mục Tồn kho.</p>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3"><input className={`${inputClass} max-w-sm`} placeholder="Tìm tên / SKU" value={query} onChange={(e) => setQuery(e.target.value)} /><button type="button" onClick={() => openForm()} className="rounded-lg bg-[#0f9d8a] px-4 py-2.5 text-sm font-bold text-white">＋ Thêm sản phẩm</button></div>
      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}
      <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
        <table className="w-full min-w-[700px] text-left text-sm"><thead><tr className="border-b border-[#24383b] text-xs text-[#92a9ad]"><th className="p-3">Sản phẩm</th><th className="p-3">SKU</th><th className="p-3">Danh mục</th><th className="p-3">Giá</th><th className="p-3">Trạng thái</th><th className="p-3">Thao tác</th></tr></thead>
          <tbody>{!loading && visibleProducts.map((product) => <tr key={product.id} className="border-b border-[#24383b] last:border-0"><td className="p-3 font-semibold">{product.name}</td><td className="p-3">{product.sku}</td><td className="p-3">{product.category_name}</td><td className="p-3">{formatPrice(product.price_vnd)}</td><td className="p-3"><button type="button" onClick={() => toggleProductStatus(product)} disabled={updatingProductIds.has(product.id)} aria-label={`Đổi trạng thái sản phẩm ${product.name}`} title="Bấm để đổi trạng thái bán" className={`rounded-full px-2.5 py-1 text-xs font-semibold disabled:cursor-wait disabled:opacity-60 ${product.is_active ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a1a1e] text-[#e5484d]'}`}>{updatingProductIds.has(product.id) ? 'Đang lưu…' : product.is_active ? 'Đang bán' : 'Ngừng bán'}</button></td><td className="p-3 whitespace-nowrap"><button type="button" className="text-[#0f9d8a]" onClick={() => openForm(product)}>Sửa</button></td></tr>)}
            {!loading && visibleProducts.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Không có sản phẩm trong backend.</td></tr>}
            {loading && <tr><td colSpan="6" className="p-8 text-center text-[#92a9ad]">Đang tải dữ liệu…</td></tr>}
          </tbody>
        </table>
      </div>

      {isProductModalOpen && <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/70 p-4"><form onSubmit={submitProduct} className="my-auto w-full max-w-2xl space-y-3 rounded-2xl border border-[#24383b] bg-[#152427] p-5"><h2 className="text-lg font-bold">{editing ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm'}</h2><div className="grid gap-3 sm:grid-cols-2"><label className="block text-xs text-[#92a9ad]">Tên sản phẩm<input className={`${inputClass} mt-1`} placeholder="Tên sản phẩm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label><label className="block text-xs text-[#92a9ad]">SKU<input className={`${inputClass} mt-1`} placeholder="SKU sản phẩm" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required /></label><label className="block text-xs text-[#92a9ad]">Danh mục<select className={`${inputClass} mt-1`} value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required><option value="">Chọn danh mục</option>{categories.filter((c) => c.is_active).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label><label className="block text-xs text-[#92a9ad]">Giá bán (₫)<input className={`${inputClass} mt-1`} type="number" min="0" placeholder="Giá bán" value={form.price_vnd} onChange={(e) => setForm({ ...form, price_vnd: e.target.value })} required /></label></div><fieldset className="rounded-lg border border-[#24383b] p-3"><legend className="px-1 text-xs text-[#92a9ad]">Màu sắc</legend>{catalogOptions.colors.length ? <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">{catalogOptions.colors.map((color) => <label key={color.id} className="flex cursor-pointer items-center gap-2 text-sm"><input type="checkbox" checked={form.selected_colors.includes(color.name)} onChange={() => toggleSelection('selected_colors', color.name)} /><span className="h-3 w-3 rounded-full border border-white/20" style={{ backgroundColor: color.hex_color }} />{color.name}</label>)}</div> : <p className="text-xs text-amber-200">Chưa có màu. Thêm màu trong mục Danh mục &amp; bảng size trước.</p>}</fieldset><fieldset className="rounded-lg border border-[#24383b] p-3"><legend className="px-1 text-xs text-[#92a9ad]">Size</legend>{catalogOptions.sizes.length ? <div className="flex flex-wrap gap-4">{catalogOptions.sizes.map((size) => <label key={size.id} className="flex cursor-pointer items-center gap-2 text-sm"><input type="checkbox" checked={form.selected_sizes.includes(size.name)} onChange={() => toggleSelection('selected_sizes', size.name)} />{size.name}</label>)}</div> : <p className="text-xs text-amber-200">Chưa có size. Thêm size trong mục Danh mục &amp; bảng size trước.</p>}</fieldset><label className="block text-xs text-[#92a9ad]">Mô tả<textarea className={`${inputClass} mt-1`} rows="2" placeholder="Mô tả sản phẩm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label><label className="block text-xs text-[#92a9ad]">Hình ảnh<input className={`${inputClass} mt-1`} type="url" placeholder="URL ảnh (không bắt buộc)" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} /></label><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />Đang kinh doanh</label>{editing && <p className="text-xs text-[#92a9ad]">Tổ hợp màu/size mới sẽ thêm biến thể; biến thể đã tạo không bị xóa khi bỏ chọn.</p>}<div className="flex justify-end gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2" onClick={() => { setProductModalOpen(false); setEditing(null); setForm(emptyForm); }}>Hủy</button><button className="rounded-lg bg-[#0f9d8a] px-4 py-2 font-bold" type="submit" disabled={!catalogOptions.colors.length || !catalogOptions.sizes.length}>Lưu sản phẩm</button></div></form></div>}

      {variantProduct && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"><form onSubmit={submitVariant} className="w-full max-w-md space-y-3 rounded-2xl border border-[#24383b] bg-[#152427] p-5"><h2 className="font-bold">Thêm biến thể · {variantProduct.name}</h2><label className="block text-xs text-[#92a9ad]">Size<select className={`${inputClass} mt-1`} value={variantForm.size} onChange={(e) => setVariantForm({ ...variantForm, size: e.target.value })} required><option value="">Chọn size</option>{catalogOptions.sizes.map((size) => <option key={size.id} value={size.name}>{size.name}</option>)}</select></label><label className="block text-xs text-[#92a9ad]">Màu<select className={`${inputClass} mt-1`} value={variantForm.color} onChange={(e) => setVariantForm({ ...variantForm, color: e.target.value })} required><option value="">Chọn màu</option>{catalogOptions.colors.map((color) => <option key={color.id} value={color.name}>{color.name}</option>)}</select></label>{(!catalogOptions.sizes.length || !catalogOptions.colors.length) && <p className="text-xs text-amber-200">Cần tạo ít nhất một size và một màu trong mục Danh mục &amp; bảng size.</p>}<input className={inputClass} placeholder="SKU biến thể" value={variantForm.sku} onChange={(e) => setVariantForm({ ...variantForm, sku: e.target.value })} required /><div className="flex justify-end gap-2"><button type="button" className="rounded-lg border border-[#24383b] px-4 py-2" onClick={() => setVariantProduct(null)}>Hủy</button><button className="rounded-lg bg-[#0f9d8a] px-4 py-2 font-bold" disabled={!catalogOptions.sizes.length || !catalogOptions.colors.length}>Tạo biến thể</button></div></form></div>}
    </div>
  );
};

export default Products;
