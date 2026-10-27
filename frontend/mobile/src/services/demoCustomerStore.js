import { getProductById } from '../data/demoProducts.js';
import { validateProfile } from '../utils/profileValidation.js';

// Mỗi tài khoản có bộ dữ liệu thử riêng trong bộ nhớ. Reload sẽ xóa dữ liệu này.
const customers = new Map();

export function getCustomerData(phone, initialProfile = {}) {
  if (!customers.has(phone)) {
    customers.set(phone, {
      profile: { name: 'Khách hàng', phone, email: '', birthday: '', height: '', weight: '', avatarUri: '', ...initialProfile },
      wishlist: [], cart: [],
    });
  }
  return customers.get(phone);
}

export function saveCustomerProfile(phone, draft) {
  const current = getCustomerData(phone);
  const profile = {
    ...current.profile,
    name: draft.name.trim(), birthday: draft.birthday.trim(),
    height: draft.height.trim(), weight: draft.weight.trim(), avatarUri: draft.avatarUri,
  };
  const error = validateProfile(profile);
  if (error) throw new Error(error);
  const next = { ...current, profile };
  customers.set(phone, next);
  return next;
}

export function toggleCustomerWishlist(phone, productId) {
  if (!getProductById(productId)) throw new Error('Sản phẩm không còn tồn tại.');
  const current = getCustomerData(phone);
  const wishlist = current.wishlist.includes(productId)
    ? current.wishlist.filter((id) => id !== productId)
    : [...current.wishlist, productId];
  const next = { ...current, wishlist };
  customers.set(phone, next);
  return next;
}

export function addCustomerCartItem(phone, productId, variantId, quantity) {
  const product = getProductById(productId);
  const variant = product?.variants.find((item) => item.id === variantId);
  if (!variant) throw new Error('Vui lòng chọn màu và kích thước hợp lệ.');
  if (!Number.isInteger(quantity) || quantity < 1) throw new Error('Số lượng phải là số nguyên lớn hơn 0.');
  const current = getCustomerData(phone);
  const existing = current.cart.find((item) => item.variantId === variantId);
  const total = (existing?.quantity || 0) + quantity;
  if (total > variant.stock) throw new Error(`Biến thể này chỉ còn ${variant.stock} sản phẩm, tính cả số đã có trong giỏ.`);
  const cart = existing
    ? current.cart.map((item) => item.variantId === variantId ? { ...item, quantity: total } : item)
    : [...current.cart, { productId, variantId, quantity }];
  const next = { ...current, cart };
  customers.set(phone, next);
  return next;
}
