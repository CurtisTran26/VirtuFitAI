import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'http://localhost:5000/api', // Tạm thời để link này, sau này có API backend thật thì sửa lại
  headers: {
    'Content-Type': 'application/json',
  },
});

// Trạm kiểm soát TRƯỚC khi GỬI request (Tự động gắn Token)
axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Trạm kiểm soát SAU khi NHẬN response (Tự động văng ra nếu Token hết hạn)
axiosClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Nếu Backend báo lỗi 401 (Phiên đăng nhập không hợp lệ / hết hạn)
    if (error.response && error.response.status === 401) {
      console.warn('Phiên đăng nhập hết hạn!');
      // Xóa sạch Token và Quyền
      localStorage.removeItem('accessToken');
      localStorage.removeItem('userRole');
      // Ép chuyển hướng về trang Đăng nhập
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosClient;