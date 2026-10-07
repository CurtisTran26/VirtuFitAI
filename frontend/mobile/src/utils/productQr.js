// Quy ước QR mẫu, cần thống nhất với backend + nhân viên kho trước tích hợp.
// Không mở trực tiếp URL quét được. Chỉ lấy ID sản phẩm từ định dạng đã cho phép.
export function getProductIdFromQr(value) {
  const text = typeof value === 'string' ? value.trim() : '';
  if (/^SP\d{3,10}$/.test(text)) return text;
  const code = text.match(/^VFIT:(SP\d{3,10})$/);
  if (code) return code[1];
  const deepLink = text.match(/^virtufit:\/\/products\/(SP\d{3,10})$/);
  if (deepLink) return deepLink[1];
  // Host .example chỉ dành cho bộ mã QR thử, thay bằng domain thật đã thống nhất.
  const webLink = text.match(/^https:\/\/virtufit\.example\/products\/(SP\d{3,10})\/?$/);
  return webLink ? webLink[1] : null;
}
