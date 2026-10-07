import { useState } from 'react';
import { Text } from 'react-native';
import AuthLayout from '../../../components/auth/AuthLayout.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import PhoneOtpFields from '../../../components/auth/PhoneOtpFields.jsx';
import usePhoneOtp from '../../../hooks/usePhoneOtp.js';
import { verifyResetOtp } from '../../../services/mockAuthService.js';
import styles from '../../../styles/authStyles.js';

export default function ForgotPasswordScreen({ navigation }) {
  const otp = usePhoneOtp('reset');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleVerify() {
    setError('');
    setLoading(true);
    try {
      const ticket = await verifyResetOtp(otp.phone, otp.code);
      navigation.replace('ResetPassword', { ticket });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Quên mật khẩu" subtitle="Nhập số điện thoại và bấm máy bay để nhận mã. Nhập mã ngay bên dưới để tiếp tục." onBack={() => navigation.goBack()}>
      <PhoneOtpFields otp={otp} disabled={loading} />
      {error !== '' && <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text>}
      <AuthButton title="Xác nhận mã" onPress={handleVerify} loading={loading} disabled={otp.sending} />
    </AuthLayout>
  );
}
