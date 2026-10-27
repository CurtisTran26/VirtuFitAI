import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import AuthLayout from '../../../components/auth/AuthLayout.jsx';
import AuthInput from '../../../components/auth/AuthInput.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import { useMobileSession } from '../../../context/MobileSessionContext.jsx';
import { signInWithGoogle } from '../../../services/googleAuthService.js';
import styles from '../../../styles/authStyles.js';

export default function LoginScreen({ navigation, route }) {
  const { signIn, acceptGoogleSession } = useMobileSession();
  const [phone, setPhone] = useState(route.params?.phone || '');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError('');
    setLoading(true);
    try {
      // Navigator tự chuyển sang nhóm màn phù hợp khi Context có user.
      await signIn(phone, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
    if (loading) return;
    setError('');
    setLoading(true);
    try {
      const session = await signInWithGoogle();
      // Hủy chọn tài khoản: giữ nguyên màn đăng nhập.
      if (session) await acceptGoogleSession(session);
    } catch (err) {
      setError(err.message || 'Không thể đăng nhập Google.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Đăng nhập">
      {route.params?.message && <Text style={styles.success}>{route.params.message}</Text>}
      <Pressable style={[styles.google, loading && { opacity: 0.5 }]} disabled={loading} accessibilityRole="button"
        onPress={handleGoogleLogin}>
        <Text style={styles.googleLetter}>G</Text>
        <Text style={styles.googleText}>Tiếp tục với Google</Text>
      </Pressable>
      <View style={styles.divider}><View style={styles.line} /><Text style={styles.dividerText}>hoặc</Text><View style={styles.line} /></View>
      <AuthInput placeholder="Số điện thoại" value={phone} onChangeText={(value) => setPhone(value.replace(/\D/g, '').slice(0, 10))} keyboardType="phone-pad" maxLength={10} editable={!loading} />
      <AuthInput placeholder="Mật khẩu" value={password} onChangeText={setPassword} password editable={!loading} />
      {error !== '' && <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text>}
      <AuthButton title="Đăng nhập" onPress={handleLogin} loading={loading} />
      <Pressable style={[styles.link, styles.right]} onPress={() => navigation.navigate('ForgotPassword')} accessibilityRole="button">
        <Text style={styles.linkText}>Quên mật khẩu?</Text>
      </Pressable>
      <View style={styles.footer}>
        <Text style={styles.footerText}>Chưa có tài khoản?</Text>
        <Pressable style={styles.link} onPress={() => navigation.navigate('Register')} accessibilityRole="button">
          <Text style={styles.linkText}>Đăng ký ngay</Text>
        </Pressable>
      </View>
    </AuthLayout>
  );
}
