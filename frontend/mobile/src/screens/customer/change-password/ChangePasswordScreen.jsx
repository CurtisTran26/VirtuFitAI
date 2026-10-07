import { useState } from 'react';
import { Text, Alert } from 'react-native';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
import AuthInput from '../../../components/auth/AuthInput.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import PhoneOtpFields from '../../../components/auth/PhoneOtpFields.jsx';
import usePhoneOtp from '../../../hooks/usePhoneOtp.js';
import { changePassword } from '../../../services/mockAuthService.js';
import { useMobileSession } from '../../../context/MobileSessionContext.jsx';
import styles from '../../../styles/customerStyles.js';

export default function ChangePasswordScreen({ navigation }) {
  const { user, signOut } = useMobileSession();
  const otp = usePhoneOtp('change', user.phone);
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleChangePassword() {
    setLoading(true);
    setError('');
    try {
      await changePassword(user.phone, otp.code, password, confirmation);
      Alert.alert('Đã đổi mật khẩu', 'Vui lòng đăng nhập lại bằng mật khẩu mới.', [{ text: 'Đăng nhập lại', onPress: signOut }], { cancelable: false });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <CustomerPage title="Đổi mật khẩu" navigation={navigation}>
      <Text style={[styles.muted, { marginBottom: 20 }]}>Gửi mã tới số điện thoại của tài khoản và nhập mật khẩu mới.</Text>
      <PhoneOtpFields otp={otp} disabled={loading} phoneEditable={false} />
      <AuthInput label="Mật khẩu mới" placeholder="Ít nhất 8 ký tự, có chữ và số" password value={password} onChangeText={setPassword} editable={!loading} />
      <AuthInput label="Nhập lại mật khẩu" placeholder="Nhập lại mật khẩu mới" password value={confirmation} onChangeText={setConfirmation} editable={!loading} />
      {error !== '' && <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text>}
      <AuthButton title="Đổi mật khẩu" onPress={handleChangePassword} loading={loading} disabled={otp.sending} />
    </CustomerPage>
  );
}
