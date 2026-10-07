import { useState } from 'react';
import { Text } from 'react-native';
import AuthLayout from '../../../components/auth/AuthLayout.jsx';
import AuthInput from '../../../components/auth/AuthInput.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import PhoneOtpFields from '../../../components/auth/PhoneOtpFields.jsx';
import usePhoneOtp from '../../../hooks/usePhoneOtp.js';
import { register } from '../../../services/mockAuthService.js';
import styles from '../../../styles/authStyles.js';

export default function RegisterScreen({ navigation }) {
  const otp = usePhoneOtp('register');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleRegister() {
    setError('');
    setLoading(true);
    try {
      await register(otp.phone, otp.code, password, confirmation);
      navigation.reset({ index: 0, routes: [{ name: 'Login', params: {
        phone: otp.phone, message: 'Đăng ký thử nghiệm thành công. Bạn có thể đăng nhập.',
      } }] });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Đăng ký" onBack={() => navigation.goBack()}>
      <PhoneOtpFields otp={otp} disabled={loading} />
      <AuthInput placeholder="Mật khẩu" password value={password} onChangeText={setPassword} editable={!loading} />
      <AuthInput placeholder="Nhập lại mật khẩu" password value={confirmation} onChangeText={setConfirmation} editable={!loading} />
      <Text style={styles.hint}>Mật khẩu ít nhất 8 ký tự, gồm chữ và số.</Text>
      {error !== '' && <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text>}
      <AuthButton title="Đăng ký" onPress={handleRegister} loading={loading} disabled={otp.sending} />
    </AuthLayout>
  );
}
