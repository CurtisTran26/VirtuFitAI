import { api, productFromApi } from './appApi.js';

export function catalogQuery(filters = {}, page = 1) {
  const entries = Object.entries({ ...filters, page, limit: 20 })
    .filter(([, value]) => value !== '' && value !== null && value !== undefined && value !== false);
  return entries.map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`).join('&');
}
export async function searchProducts(filters, page = 1) {
  const result = await api(`/catalog/products?${catalogQuery(filters, page)}`, { anonymous: true });
  if (!Array.isArray(result.items) || !Number.isInteger(result.total)) throw new Error('Danh sách sản phẩm không hợp lệ.');
  return { ...result, items: result.items.map(productFromApi) };
}
export const loadCategories = () => api('/catalog/categories', { anonymous: true });
export const loadFilterOptions = categoryId => api(`/catalog/filter-options${categoryId ? `?category_id=${encodeURIComponent(categoryId)}` : ''}`, { anonymous: true });

export function validatePriceRange(min, max) {
  for (const value of [min, max]) {
    if (value !== '' && (!/^\d+$/.test(value) || !Number.isSafeInteger(Number(value)))) return 'Giá phải là số nguyên VNĐ không âm.';
  }
  if (min !== '' && max !== '' && Number(min) > Number(max)) return 'Giá tối thiểu phải nhỏ hơn hoặc bằng giá tối đa.';
  return '';
}
