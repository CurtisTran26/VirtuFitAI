import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Client ID là định danh công khai. KHÔNG đưa Google client secret vào app.
const WEB_CLIENT_ID = process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID;
const IOS_CLIENT_ID = process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID;
const API_URL = process.env.EXPO_PUBLIC_APP_API_URL;

export async function signInWithGoogle() {
  if (Constants.executionEnvironment === 'storeClient') {
    throw new Error('Google Login cần development build. Bạn đang mở bằng Expo Go.');
  }
  if (Platform.OS !== 'android' && Platform.OS !== 'ios') {
    throw new Error('Ví dụ này dành cho app Android và iOS.');
  }
  if (!WEB_CLIENT_ID || !WEB_CLIENT_ID.endsWith('.apps.googleusercontent.com')) {
    throw new Error('Chưa điền EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID trong file .env.');
  }
  if (Platform.OS === 'ios' && !IOS_CLIENT_ID) {
    throw new Error('Chưa điền EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID.');
  }

  // Chỉ nạp native module sau khi đã kiểm tra môi trường chạy.
  const { GoogleSignin, statusCodes } = require('@react-native-google-signin/google-signin');
  GoogleSignin.configure({ webClientId: WEB_CLIENT_ID, iosClientId: IOS_CLIENT_ID, offlineAccess: false });

  let result;
  try {
    if (Platform.OS === 'android') await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
    // Cho chọn lại tài khoản, kể cả sau khi đăng xuất khỏi VirtuFitAI.
    await GoogleSignin.signOut();
    result = await GoogleSignin.signIn();
  } catch (error) {
    if (error.code === statusCodes.SIGN_IN_CANCELLED) return null;
    if (error.code === statusCodes.IN_PROGRESS) throw new Error('Yêu cầu Google đang được xử lý.');
    if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) throw new Error('Thiết bị cần Google Play Services để đăng nhập.');
    throw new Error(`Không đăng nhập được Google (${error.code || 'không rõ mã lỗi'}). Kiểm tra Client ID, package name và SHA-1.`);
  }
  if (result.type === 'cancelled') return null;
  if (result.type !== 'success' || !result.data?.idToken) {
    throw new Error('Google chưa trả ID token. Kiểm tra Web Client ID.');
  }
  if (!API_URL) {
    // Google chạy được vẫn chưa có nghĩa là đã có phiên đăng nhập ở backend.
    throw new Error(`Đã xác thực Google: ${result.data.user.email}. Chưa có app-api nên chưa đăng nhập vào VirtuFitAI. Cần cấu hình EXPO_PUBLIC_APP_API_URL.`);
  }
  if (!API_URL.startsWith('https://')) {
    throw new Error('APP_API_URL cần dùng HTTPS để gửi token đăng nhập.');
  }

  // Backend xác minh ID token, tìm/tạo customer, rồi phát token của VirtuFitAI.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${API_URL.replace(/\/$/, '')}/auth/google`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: result.data.idToken }), signal: controller.signal,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(typeof data?.detail === 'string' ? data.detail : 'Backend từ chối đăng nhập Google.');
    }
    if (!data) throw new Error('Backend chưa trả dữ liệu JSON hợp lệ.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Kết nối backend quá lâu. Vui lòng thử lại.');
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
