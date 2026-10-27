// Quy tắc tạm thời, cần thống nhất với backend trước khi nối API.
export function validatePhone(phone) {
  return /^0[35789]\d{8}$/.test(phone)
    ? '' : 'Nhập số điện thoại Việt Nam gồm 10 số, bắt đầu bằng 0.';
}

export function validatePassword(password, confirmation) {
  if (password.length < 8 || !/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
    return 'Mật khẩu cần ít nhất 8 ký tự, gồm chữ và số.';
  }
  if (password !== confirmation) return 'Mật khẩu nhập lại chưa khớp.';
  return '';
}

export function formatTime(seconds) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
}
