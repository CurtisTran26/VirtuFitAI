import { demoProducts, formatPrice } from '../data/demoProducts.js';

// Đây là câu trả lời theo từ khóa để thử giao diện, KHÔNG phải mô hình AI.
// Khi có backend, thay hàm này bằng lời gọi app-api. Không để API key AI trong app.
export function getDemoAiReply(message) {
  const text = message.toLowerCase();
  if (text.includes('giá') || text.includes('sản phẩm')) {
    return 'Giá mẫu hiện tại:\n' + demoProducts.map((item) => `${item.name}: ${formatPrice(item.price)}`).join('\n');
  }
  if (text.includes('size') || text.includes('kích thước')) {
    return 'Bạn có thể xem các size ở trang chi tiết sản phẩm. Gợi ý size cá nhân sẽ có khi nhóm nối chức năng tương ứng.';
  }
  if (text.includes('thử')) return 'Mở sản phẩm bạn thích để xem thông tin. Chức năng thử đồ AI đang chờ tích hợp dịch vụ xử lý ảnh.';
  if (text.includes('thiết kế')) return 'Mục Thiết kế sẽ nhận yêu cầu trang phục của bạn. Luồng tạo thiết kế và gửi designer đang được phát triển.';
  return 'Mình đang ở chế độ minh họa. Bạn thử hỏi “Giá sản phẩm”, “Chọn size” hoặc “Thử đồ” để kiểm tra giao diện chat nhé.';
}
