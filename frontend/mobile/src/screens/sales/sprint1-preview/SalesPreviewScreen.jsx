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
      <Text style={styles.subtitle}>Xin chào {user.full_name || user.phone}. Khu vực bán hàng tạm thời chưa khả dụng.</Text>
      <AuthButton title="Đăng xuất" onPress={signOut} />
    </AuthLayout>
  );
}
