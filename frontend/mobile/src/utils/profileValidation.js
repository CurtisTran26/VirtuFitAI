export function validateProfile(profile) {
  if (!profile.name.trim()) return 'Vui lòng nhập họ và tên.';
  if (profile.name.trim().length > 80) return 'Họ và tên tối đa 80 ký tự.';
  // Số điện thoại đăng nhập và email Google không chỉnh trực tiếp trong form hồ sơ.
  if (profile.birthday) {
    const parts = profile.birthday.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    if (!parts) return 'Ngày sinh cần có dạng ngày/tháng/năm, ví dụ 20/08/2004.';
    const day = Number(parts[1]);
    const month = Number(parts[2]);
    const year = Number(parts[3]);
    const date = new Date(year, month - 1, day);
    if (date.getDate() !== day || date.getMonth() !== month - 1 || date.getFullYear() !== year || date > new Date()) {
      return 'Ngày sinh không hợp lệ hoặc nằm trong tương lai.';
    }
  }
  if (profile.height && (!Number.isFinite(Number(profile.height)) || Number(profile.height) < 50 || Number(profile.height) > 250)) {
    return 'Chiều cao phải từ 50 đến 250 cm.';
  }
  if (profile.weight && (!Number.isFinite(Number(profile.weight)) || Number(profile.weight) < 10 || Number(profile.weight) > 300)) {
    return 'Cân nặng phải từ 10 đến 300 kg.';
  }
  return '';
}
