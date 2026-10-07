import { useState } from 'react';
import { Text } from 'react-native';
import AuthLayout from '../../../components/auth/AuthLayout.jsx';
import AuthInput from '../../../components/auth/AuthInput.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import { resetPassword } from '../../../services/mockAuthService.js';
import styles from '../../../styles/authStyles.js';

export default function ResetPasswordScreen({ navigation, route }) {
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleReset() {
    setError('');
    setLoading(true);
    try {
      const phone = await resetPassword(route.params?.ticket, password, confirmation);
      navigation.reset({ index: 0, routes: [{ name: 'Login', params: {
        phone, message: 'Đã đổi mật khẩu thử nghiệm. Hãy đăng nhập lại.',
      } }] });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Đặt mật khẩu mới" onBack={() => navigation.replace('ForgotPassword')}>
      <AuthInput label="Mật khẩu mới" placeholder="Nhập mật khẩu mới" password value={password} onChangeText={setPassword} editable={!loading} />
      <Text style={styles.hint}>Mật khẩu ít nhất 8 ký tự, gồm chữ và số.</Text>
      <AuthInput label="Xác nhận mật khẩu" placeholder="Nhập lại mật khẩu mới" password value={confirmation} onChangeText={setConfirmation} editable={!loading} />
      {error !== '' && <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text>}
      <AuthButton title="Lưu mật khẩu mới" onPress={handleReset} loading={loading} />
    </AuthLayout>
  );
}
