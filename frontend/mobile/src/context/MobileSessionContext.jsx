import { createContext, useContext, useState } from 'react';
import { login } from '../services/mockAuthService.js';
import { getCustomerData, saveCustomerProfile, toggleCustomerWishlist, addCustomerCartItem } from '../services/demoCustomerStore.js';

const MobileSessionContext = createContext(null);

export function MobileSessionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [customerData, setCustomerData] = useState(null);

  async function signIn(phone, password) {
    const result = await login(phone, password);
    // Backend thật phải trả role đã xác thực, không lấy role từ form người dùng.
    setCustomerData(result.role === 'customer' ? getCustomerData(result.phone) : null);
    setUser(result);
  }

  // Chỉ gọi sau khi app-api đã xác minh Google ID token và trả phiên đăng nhập.
  // Đây không phải cách tự gán vai trò từ email hoặc từ thông tin Google trên máy.
  function acceptGoogleSession(session) {
    const account = session?.user;
    if (typeof session?.access_token !== 'string' || !session.access_token ||
        !account?.id || account.role !== 'customer' || typeof account.email !== 'string') {
      throw new Error('Kết quả đăng nhập Google từ backend chưa đúng định dạng khách hàng.');
    }
    const storageKey = `google:${account.id}`;
    setCustomerData(getCustomerData(storageKey, {
      name: account.name || 'Khách hàng', email: account.email,
      phone: account.phone || '', avatarUri: account.avatar_url || '',
    }));
    // Token chỉ nằm trong bộ nhớ của phiên này. Đóng app cần đăng nhập lại.
    setUser({ ...account, storageKey, authMethod: 'google', accessToken: session.access_token });
  }

  function signOut() {
    setUser(null);
    setCustomerData(null);
  }

  function saveProfile(draft) {
    setCustomerData(saveCustomerProfile(user.storageKey || user.phone, draft));
  }

  function toggleWishlist(id) {
    setCustomerData(toggleCustomerWishlist(user.storageKey || user.phone, id));
  }

  function addToCart(productId, variantId, quantity) {
    setCustomerData(addCustomerCartItem(user.storageKey || user.phone, productId, variantId, quantity));
  }

  return (
    <MobileSessionContext.Provider value={{ user, customerData, signIn, acceptGoogleSession, signOut, saveProfile, toggleWishlist, addToCart }}>
      {children}
    </MobileSessionContext.Provider>
  );
}

export function useMobileSession() {
  return useContext(MobileSessionContext);
}
