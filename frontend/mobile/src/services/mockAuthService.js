// CHỈ dùng thử giao diện. Không gửi SMS, không gọi API, không lưu dữ liệu vào máy.
// Không dùng thông tin thật. Tải lại ứng dụng sẽ mất tài khoản vừa tạo.
// Khi có backend: thay các hàm này bằng lời gọi app-api. OTP do server kiểm tra.
import { validatePhone, validatePassword } from '../utils/authValidation.js';

export const DEMO_PHONE = '0901234567';
export const DEMO_SALES_PHONE = '0900000002';
export const DEMO_PASSWORD = 'Demo1234';
export const DEMO_OTP = '123456';
export const RESEND_SECONDS = 45;
export const OTP_SECONDS = 300;
const accounts = new Map([[DEMO_PHONE, DEMO_PASSWORD], [DEMO_SALES_PHONE, DEMO_PASSWORD]]);
const otpRequests = new Map();
const resetTickets = new Map();
let ticketNumber = 0;

function requireValidPhone(phone) {
  const error = validatePhone(phone);
  if (error) throw new Error(error);
}

export async function sendOtp(phone, purpose) {
  requireValidPhone(phone);
  if (!['register', 'reset', 'change'].includes(purpose)) throw new Error('Mục đích gửi OTP không hợp lệ.');
  if (purpose === 'register' && accounts.has(phone)) {
    throw new Error('Số điện thoại đã có tài khoản thử nghiệm. Vui lòng đăng nhập.');
  }
  if (purpose !== 'register' && !accounts.has(phone)) {
    throw new Error('Chưa có tài khoản thử nghiệm với số này. Hãy đăng ký trước.');
  }
  const key = `${purpose}:${phone}`;
  const oldRequest = otpRequests.get(key);
  const now = Date.now();
  if (oldRequest && now < oldRequest.resendAt) {
    throw new Error('Vui lòng chờ hết thời gian trước khi gửi lại mã.');
  }
  const request = {
    expiresAt: now + OTP_SECONDS * 1000,
    resendAt: now + RESEND_SECONDS * 1000,
  };
  otpRequests.set(key, request);
  return request;
}

function checkOtp(phone, purpose, code) {
  const request = otpRequests.get(`${purpose}:${phone}`);
  if (!request) throw new Error('Hãy bấm nút máy bay để gửi mã trước.');
  if (Date.now() >= request.expiresAt) throw new Error('Mã đã hết hạn. Vui lòng gửi lại.');
  if (code !== DEMO_OTP) throw new Error('Mã xác nhận không đúng. Vui lòng thử lại.');
}

export async function register(phone, code, password, confirmation) {
  requireValidPhone(phone);
  const error = validatePassword(password, confirmation);
  if (error) throw new Error(error);
  if (accounts.has(phone)) throw new Error('Số điện thoại đã được đăng ký.');
  checkOtp(phone, 'register', code);
  accounts.set(phone, password);
  otpRequests.delete(`register:${phone}`);
}

export async function login(phone, password) {
  requireValidPhone(phone);
  if (accounts.get(phone) !== password) {
    throw new Error('Số điện thoại hoặc mật khẩu chưa đúng.');
  }
  return { phone, role: phone === DEMO_SALES_PHONE ? 'sales' : 'customer' };
}

export async function verifyResetOtp(phone, code) {
  checkOtp(phone, 'reset', code);
  // Vé giả lập giúp màn đặt mật khẩu chỉ hoạt động sau bước xác nhận OTP.
  // Backend thật phải cấp token an toàn, có hạn dùng và chỉ dùng được một lần.
  const ticket = `demo-reset-${++ticketNumber}`;
  resetTickets.set(ticket, { phone, expiresAt: Date.now() + OTP_SECONDS * 1000 });
  otpRequests.delete(`reset:${phone}`);
  return ticket;
}

export async function resetPassword(ticket, password, confirmation) {
  const error = validatePassword(password, confirmation);
  if (error) throw new Error(error);
  const request = resetTickets.get(ticket);
  if (!request || Date.now() >= request.expiresAt) {
    throw new Error('Phiên đặt mật khẩu đã hết hạn. Hãy quay lại gửi mã mới.');
  }
  accounts.set(request.phone, password);
  resetTickets.delete(ticket);
  return request.phone;
}

export async function changePassword(phone, code, password, confirmation) {
  const error = validatePassword(password, confirmation);
  if (error) throw new Error(error);
  if (!accounts.has(phone)) throw new Error('Tài khoản không tồn tại.');
  checkOtp(phone, 'change', code);
  accounts.set(phone, password);
  otpRequests.delete(`change:${phone}`);
}
