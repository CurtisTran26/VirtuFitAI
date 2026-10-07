import { Text } from 'react-native';
import AuthLayout from '../../../components/auth/AuthLayout.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import { useMobileSession } from '../../../context/MobileSessionContext.jsx';
import styles from '../../../styles/authStyles.js';

// Chỉ kiểm tra điều hướng role. Các màn bán hàng thật thuộc phần ghép của Lộc.
export default function SalesPreviewScreen() {
  const { user, signOut } = useMobileSession();
  return (
    <AuthLayout title="Nhân viên bán hàng">
      <Text style={styles.subtitle}>Tài khoản thử: {user.phone}. Đã chuyển đúng khu vực nhân viên. Dashboard bán hàng sẽ được nối sau.</Text>
      <AuthButton title="Đăng xuất" onPress={signOut} />
    </AuthLayout>
  );
}
