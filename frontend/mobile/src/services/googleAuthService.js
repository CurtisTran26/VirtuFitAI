import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Client ID là định danh công khai. KHÔNG đưa Google client secret vào app.
const WEB_CLIENT_ID = process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID;
const IOS_CLIENT_ID = process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID;
import { api } from './appApi.js';

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
  return api('/auth/google', { method: 'POST', anonymous: true, body: { id_token: result.data.idToken } });
}
