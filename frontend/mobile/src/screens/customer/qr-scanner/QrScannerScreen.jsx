import { useEffect, useRef, useState } from 'react';
import { View, Text, Pressable, Alert, Linking, AppState } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useIsFocused } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import { getProductIdFromQr } from '../../../utils/productQr.js';
import { getProductById } from '../../../data/demoProducts.js';
import styles from '../../../styles/customerStyles.js';

export default function QrScannerScreen({ navigation }) {
  const [permission, requestPermission, getPermission] = useCameraPermissions();
  const [torch, setTorch] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [appActive, setAppActive] = useState(AppState.currentState === 'active');
  const [paused, setPaused] = useState(false);
  const isFocused = useIsFocused();
  // Ref chặn ngay callback liên tiếp, không phải chờ React cập nhật state.
  const scanLocked = useRef(false);

  useEffect(() => {
    const subscription = AppState.addEventListener('change', (state) => {
      setAppActive(state === 'active');
      // Đọc lại quyền khi quay về từ Cài đặt hệ thống.
      if (state === 'active') getPermission().catch(() => setCameraError('Không đọc được quyền camera.'));
    });
    return () => subscription.remove();
  }, [getPermission]);

  function resumeScan() {
    scanLocked.current = false;
    setPaused(false);
  }

  function handleScanned({ data }) {
    if (scanLocked.current) return;
    scanLocked.current = true;
    setPaused(true);
    const id = getProductIdFromQr(data);
    if (!id || !getProductById(id)) {
      Alert.alert('Không tìm thấy sản phẩm', 'Mã QR không hợp lệ hoặc sản phẩm chưa có trong bộ dữ liệu thử.', [{ text: 'Quét lại', onPress: resumeScan }], { cancelable: false });
      return;
    }
    navigation.replace('ProductDetail', { productId: id });
  }

  async function allowCamera() {
    setCameraError('');
    try {
      if (permission?.canAskAgain === false) await Linking.openSettings();
      else await requestPermission();
    } catch {
      setCameraError('Không mở được quyền camera. Hãy kiểm tra trong cài đặt thiết bị.');
    }
  }

  if (!permission) return <CustomerPage title="Quét QR" navigation={navigation}><Text style={styles.text}>Đang kiểm tra quyền camera…</Text></CustomerPage>;

  if (!permission.granted || cameraError) {
    return (
      <CustomerPage title="Quét QR" navigation={navigation}>
        <View style={styles.empty}>
          <Ionicons name="camera-outline" size={60} color="#777" />
          <Text style={[styles.text, styles.centerText]}>{cameraError || 'Cho phép dùng camera để quét mã QR trên sản phẩm.'}</Text>
          <AuthButton title={cameraError && permission.granted ? 'Thử lại camera' : permission.canAskAgain ? 'Cho phép camera' : 'Mở cài đặt'} onPress={cameraError && permission.granted ? () => setCameraError('') : allowCamera} />
          <AuthButton title="Xem sản phẩm mẫu" onPress={() => navigation.replace('ProductDetail', { productId: 'SP001' })} />
        </View>
      </CustomerPage>
    );
  }

  return (
    <CustomerPage title="Quét QR sản phẩm" navigation={navigation} scroll={false}
      rightElement={<Pressable style={styles.iconButton} onPress={() => setTorch(!torch)} accessibilityRole="button" accessibilityLabel={torch ? 'Tắt đèn pin' : 'Bật đèn pin'}><Ionicons name={torch ? 'flash' : 'flash-outline'} size={23} color="#111" /></Pressable>}>
      <View style={styles.cameraFrame}>
        {/* Camera chỉ hoạt động khi màn này đang được xem và app ở foreground. */}
        {isFocused && appActive && <CameraView style={styles.flex} facing="back" enableTorch={torch}
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
          onBarcodeScanned={paused ? undefined : handleScanned}
          onMountError={() => setCameraError('Không khởi động được camera. Vui lòng thử lại.')} />}
        <View style={styles.cameraOverlay} pointerEvents="none">
          <View style={styles.scanBox} /><Text style={styles.scanHint}>Đặt mã QR trước camera</Text>
        </View>
      </View>
      <View style={styles.cameraActions}>
        <Text style={[styles.muted, styles.centerText]}>Dùng các mã trong thư mục QR-MAU của gói để thử.</Text>
        <AuthButton title="Xem sản phẩm mẫu (không quét)" onPress={() => navigation.replace('ProductDetail', { productId: 'SP001' })} />
      </View>
    </CustomerPage>
  );
}
