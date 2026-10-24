export const API_URL = (process.env.EXPO_PUBLIC_INTEGRATION_API_URL || 'http://10.0.2.2:8000/api/v1').replace(/\/$/, '');
let sessionToken = null;
let onExpired = null;
export function setApiSession(token, expired) { sessionToken = token; onExpired = expired || null; }

export async function api(path, { method = 'GET', body, token = sessionToken, anonymous = false } = {}) {
  if (!API_URL.startsWith('https://') && !(typeof __DEV__ !== 'undefined' && __DEV__ && /^http:\/\/(10\.0\.2\.2|localhost|127\.0\.0\.1):\d+\/api\/v1$/.test(API_URL))) {
    throw new Error('API cần HTTPS; địa chỉ HTTP cục bộ chỉ dùng trong development build.');
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      method, signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(!anonymous && token ? { Authorization: `Bearer ${token}` } : {}) },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401 && !anonymous && token === sessionToken) onExpired?.();
      throw new Error(data?.error?.message || (typeof data?.detail === 'string' && data.detail) || `Yêu cầu thất bại (${response.status}).`);
    }
    if (response.status !== 204 && data === null) throw new Error('Máy chủ trả dữ liệu không hợp lệ.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Máy chủ phản hồi quá lâu. Vui lòng thử lại.');
    if (error instanceof TypeError) throw new Error('Không kết nối được máy chủ. Vui lòng thử lại sau.');
    throw error;
  } finally { clearTimeout(timer); }
}

export async function allPages(path, options = {}) {
  const items = [];
  for (let page = 1; ; page++) {
    const result = await api(`${path}${path.includes('?') ? '&' : '?'}page=${page}&limit=100`, options);
    items.push(...result.items);
    if (items.length >= result.total || result.items.length === 0) return items;
  }
}

export function productFromApi(p) {
  const variants = (p.variants || []).map(v => ({ ...v, stock: v.stock_on_hand }));
  return { ...p, price: Number(p.price_vnd), imageSource: p.image_url ? { uri: p.image_url } : null,
    variants, colors: [...new Set(variants.map(v => v.color))], sizes: [...new Set(variants.map(v => v.size))] };
}
export const formatPrice = value => `${Number(value || 0).toLocaleString('vi-VN')} ₫`;
export const getVariant = (product, color, size) => product.variants.find(v => v.color === color && v.size === size);
export function profileFromApi(p) {
  return { name: p.full_name || '', phone: p.phone || '', email: p.email || '',
    birthday: p.date_of_birth ? p.date_of_birth.split('-').reverse().join('/') : '',
    height: p.height_cm == null ? '' : String(p.height_cm), weight: p.weight_kg == null ? '' : String(p.weight_kg), avatarUri: p.avatar_url || '' };
}
