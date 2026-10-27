import { api } from './appApi.js';
import { validatePhone, validatePassword } from '../utils/authValidation.js';
function phoneCheck(phone) { const error = validatePhone(phone); if (error) throw new Error(error); }
function passwordCheck(password, confirmation) {
  const error = validatePassword(password, confirmation); if (error) throw new Error(error);
}
export const login = (phone, password) => api('/auth/login', { method: 'POST', anonymous: true, body: { phone: phone.trim(), password } });
export const logout = token => api('/auth/logout', { method: 'POST', token });
export async function sendOtp(phone, purpose) {
  phoneCheck(phone);
  const result = await api('/auth/otp', { method: 'POST', anonymous: purpose !== 'change',
    body: { phone, purpose: { register: 'register', reset: 'reset_password', change: 'change_password' }[purpose] } });
  return { resendAt: Date.now() + result.resend_after * 1000, expiresAt: Date.now() + result.expires_in * 1000,
    debugCode: typeof __DEV__ !== 'undefined' && __DEV__ ? result.debug_code : null };
}
export async function register(phone, code, password, confirmation, fullName) {
  phoneCheck(phone); passwordCheck(password, confirmation);
  if (!fullName?.trim()) throw new Error('Vui lòng nhập họ và tên.');
  // Registration issues a session. Revoke it before returning to Login.
  const session = await api('/auth/register', { method: 'POST', anonymous: true,
    body: { phone, otp_code: code, password, full_name: fullName.trim() } });
  try { await logout(session.access_token); } catch { /* The short-lived registration session is not used by the UI. */ }
}
export const verifyResetOtp = (phone, code) => api('/auth/verify-reset-otp', { method: 'POST', anonymous: true, body: { phone, otp_code: code } });
export async function resetPassword(ticket, password, confirmation) {
  passwordCheck(password, confirmation);
  if (!ticket?.reset_token) throw new Error('Vui lòng xác minh OTP lại.');
  await api('/auth/reset-password', { method: 'POST', anonymous: true, body: { reset_token: ticket.reset_token, new_password: password } });
  return ticket.phone;
}
export async function changePassword(phone, code, password, confirmation) {
  passwordCheck(password, confirmation);
  await api('/auth/change-password', { method: 'POST', body: { otp_code: code, new_password: password } });
}
