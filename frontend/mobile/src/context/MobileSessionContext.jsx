import { createContext, useCallback, useContext, useRef, useState } from 'react';
import { api, allPages, productFromApi, profileFromApi, setApiSession } from '../services/appApi.js';
import { login, logout } from '../services/authApiService.js';
import { validateProfile } from '../utils/profileValidation.js';

const MobileSessionContext = createContext(null);
export function MobileSessionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [customerData, setCustomerData] = useState(null);
  const [products, setProducts] = useState([]);
  const [catalogError, setCatalogError] = useState('');
  const [catalogLoading, setCatalogLoading] = useState(false);
  const generation = useRef(0);
  const wishlistBusy = useRef(new Set());

  function clearSession() {
    generation.current += 1;
    setApiSession(null); setUser(null); setCustomerData(null); setProducts([]);
    setCatalogError(''); setCatalogLoading(false); wishlistBusy.current.clear();
  }
  async function acceptSession(session, authMethod) {
    const account = session?.user;
    if (!account?.id || !account.role || typeof session.access_token !== 'string' || !session.access_token) throw new Error('Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.');
    const revision = ++generation.current;
    const token = session.access_token;
    try {
      const profile = await api('/users/me', { token });
      const wishlist = account.role === 'customer' ? await allPages('/wishlist', { token }) : [];
      if (revision !== generation.current) return;
      setApiSession(token, clearSession);
      setCustomerData({ profile: profileFromApi(profile), wishlist: wishlist.map(p => p.id), wishlistProducts: wishlist.map(productFromApi), cart: [] });
      setUser({ ...account, authMethod, accessToken: token });
    } catch (error) {
      try { await logout(token); } catch { /* Preserve the original initialization error. */ }
      throw error;
    }
  }
  async function signIn(phone, password) { await acceptSession(await login(phone, password), 'phone'); }
  async function acceptGoogleSession(session) { await acceptSession(session, 'google'); }
  async function signOut() {
    const token = user?.accessToken; clearSession();
    if (token) try { await logout(token); } catch { console.warn('Đã thoát trên máy; chưa thu hồi được phiên server do lỗi kết nối.'); }
  }
  async function refreshCatalog() {
    const revision = generation.current; setCatalogLoading(true); setCatalogError('');
    try {
      const rows = await allPages('/catalog/products');
      if (revision === generation.current) setProducts(rows.map(productFromApi));
    } catch (error) { if (revision === generation.current) setCatalogError(error.message); }
    finally { if (revision === generation.current) setCatalogLoading(false); }
  }
  async function loadProduct(id) {
    const revision = generation.current;
    const product = productFromApi(await api(`/catalog/products/${encodeURIComponent(id)}`));
    if (revision === generation.current) setProducts(current => [...current.filter(p => p.id !== product.id), product]);
    return product;
  }
  const refreshProfile = useCallback(async () => {
    const revision = generation.current;
    const profile = await api('/users/me');
    if (revision === generation.current) setCustomerData(current => current ? { ...current, profile: profileFromApi(profile) } : current);
  }, []);
  async function saveProfile(draft) {
    const error = validateProfile(draft); if (error) throw new Error(error);
    const revision = generation.current;
    const body = { full_name: draft.name.trim(), date_of_birth: draft.birthday ? draft.birthday.split('/').reverse().join('-') : null,
      height_cm: draft.height ? Number(draft.height) : null, weight_kg: draft.weight ? Number(draft.weight) : null };
    if (draft.avatarData !== undefined) body.avatar_data = draft.avatarData;
    const saved = await api('/users/me', { method: 'PUT', body });
    if (revision === generation.current) setCustomerData(current => ({ ...current, profile: profileFromApi(saved) }));
  }
  async function toggleWishlist(id) {
    if (wishlistBusy.current.has(id)) return;
    wishlistBusy.current.add(id); const revision = generation.current;
    try {
      const selected = customerData.wishlist.includes(id);
      await api(`/wishlist/${encodeURIComponent(id)}`, { method: selected ? 'DELETE' : 'PUT' });
      const rows = await allPages('/wishlist');
      if (revision === generation.current) setCustomerData(current => ({ ...current, wishlist: rows.map(p => p.id), wishlistProducts: rows.map(productFromApi) }));
    } finally { wishlistBusy.current.delete(id); }
  }
  function addToCart(productId, variantId, quantity) {
    const product = products.find(p => p.id === productId);
    const variant = product?.variants.find(v => v.id === variantId);
    if (!variant || !Number.isInteger(quantity) || quantity < 1) throw new Error('Vui lòng chọn màu, kích thước và số lượng.');
    const previous = customerData.cart.find(i => i.variantId === variantId);
    if ((previous?.quantity || 0) + quantity > variant.stock) throw new Error('Số lượng vượt quá tồn kho đang hiển thị.');
    // Sprint 1 selection preview only; not checkout or an inventory reservation.
    setCustomerData(current => ({ ...current, cart: previous ? current.cart.map(i => i.variantId === variantId ? { ...i, quantity: i.quantity + quantity } : i) : [...current.cart, { productId, variantId, quantity, product, variant }] }));
  }
  return <MobileSessionContext.Provider value={{ user, customerData, products, catalogError, catalogLoading, refreshCatalog, loadProduct,
    signIn, acceptGoogleSession, signOut, saveProfile, refreshProfile, toggleWishlist, addToCart }}>{children}</MobileSessionContext.Provider>;
}
export function useMobileSession() { return useContext(MobileSessionContext); }
