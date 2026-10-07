import { StatusBar, Text } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MobileSessionProvider, useMobileSession } from '../context/MobileSessionContext.jsx';
import WelcomeScreen from '../screens/auth/welcome/WelcomeScreen.jsx';
import LoginScreen from '../screens/auth/login/LoginScreen.jsx';
import RegisterScreen from '../screens/auth/register/RegisterScreen.jsx';
import ForgotPasswordScreen from '../screens/auth/forgot-password/ForgotPasswordScreen.jsx';
import ResetPasswordScreen from '../screens/auth/reset-password/ResetPasswordScreen.jsx';
import HomeScreen from '../screens/customer/home/HomeScreen.jsx';
import AiChatScreen from '../screens/customer/chat/AiChatScreen.jsx';
import FeaturePendingScreen from '../screens/customer/feature-pending/FeaturePendingScreen.jsx';
import ProfileScreen from '../screens/customer/profile/ProfileScreen.jsx';
import EditProfileScreen from '../screens/customer/edit-profile/EditProfileScreen.jsx';
import ChangePasswordScreen from '../screens/customer/change-password/ChangePasswordScreen.jsx';
import ProductDetailScreen from '../screens/customer/product-detail/ProductDetailScreen.jsx';
import QrScannerScreen from '../screens/customer/qr-scanner/QrScannerScreen.jsx';
import WishlistScreen from '../screens/customer/wishlist/WishlistScreen.jsx';
import CartPreviewScreen from '../screens/customer/cart-preview/CartPreviewScreen.jsx';
import SalesPreviewScreen from '../screens/sales/sprint1-preview/SalesPreviewScreen.jsx';
import AuthLayout from '../components/auth/AuthLayout.jsx';
import AuthButton from '../components/auth/AuthButton.jsx';

const Stack = createNativeStackNavigator();

function UnsupportedRoleScreen() {
  const { signOut } = useMobileSession();
  return <AuthLayout title="Vai trò chưa được hỗ trợ"><Text>Tài khoản này không có khu vực sử dụng trên app.</Text><AuthButton title="Đăng xuất" onPress={signOut} /></AuthLayout>;
}

function RoleNavigator() {
  const { user } = useMobileSession();
  return (
    <NavigationContainer>
      {/* Đổi key khi đăng nhập/đăng xuất để xóa lịch sử màn của phiên cũ. */}
      <Stack.Navigator key={user ? `${user.role}:${user.id || user.phone}` : 'signed-out'} screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#fff' } }}>
        {!user ? (
          <>
            <Stack.Screen name="Welcome" component={WelcomeScreen} />
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
            <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
            <Stack.Screen name="ResetPassword" component={ResetPasswordScreen} />
          </>
        ) : user.role === 'customer' ? (
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="AiChat" component={AiChatScreen} />
            <Stack.Screen name="FeaturePending" component={FeaturePendingScreen} />
            <Stack.Screen name="Profile" component={ProfileScreen} />
            <Stack.Screen name="EditProfile" component={EditProfileScreen} />
            <Stack.Screen name="ChangePassword" component={ChangePasswordScreen} />
            <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
            <Stack.Screen name="QrScanner" component={QrScannerScreen} />
            <Stack.Screen name="Wishlist" component={WishlistScreen} />
            <Stack.Screen name="CartPreview" component={CartPreviewScreen} />
          </>
        ) : user.role === 'sales' ? (
          <Stack.Screen name="SalesPreview" component={SalesPreviewScreen} />
        ) : <Stack.Screen name="UnsupportedRole" component={UnsupportedRoleScreen} />}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function AuthNavigator() {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" />
      <MobileSessionProvider><RoleNavigator /></MobileSessionProvider>
    </SafeAreaProvider>
  );
}
