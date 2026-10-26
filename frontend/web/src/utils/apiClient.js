const API_BASE_URL = (import.meta.env.VITE_MANAGEMENT_API_BASE_URL || 'http://localhost:8001/api/v1').replace(/\/$/, '');
const localizedErrors = {
  OUT_OF_STOCK: 'Không thể xuất nhiều hơn số lượng tồn hiện có.',
  STOCK_RESERVED: 'Không thể giảm tồn kho thấp hơn số lượng đang được giữ cho đơn hàng.',
  VARIANT_NOT_FOUND: 'Không tìm thấy biến thể sản phẩm trong kho.',
  VARIANT_HAS_STOCK: 'Không thể xóa biến thể còn tồn kho. Hãy xử lý tồn kho về 0 trước.',
  VARIANT_IN_USE: 'Không thể xóa biến thể vì đã có lịch sử tồn kho hoặc đơn hàng liên quan.',
};

const request = async (path, options = {}) => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${API_BASE_URL}/${path.replace(/^\//, '')}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401 && path !== 'auth/staff-login') {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');
    window.location.assign('/login');
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const code = data?.error?.code || data?.detail?.code;
    const message = localizedErrors[code] || data?.error?.message || data?.detail?.message || `Lỗi yêu cầu (${response.status}).`;
    throw new Error(message);
  }

  return data;
};

const apiClient = {
  get: (path, options) => request(path, options),
  post: (path, body, options = {}) => request(path, { ...options, method: 'POST', body: JSON.stringify(body) }),
  patch: (path, body, options = {}) => request(path, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  put: (path, body, options = {}) => request(path, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  delete: (path, options = {}) => request(path, { ...options, method: 'DELETE' }),
};

export default apiClient;
