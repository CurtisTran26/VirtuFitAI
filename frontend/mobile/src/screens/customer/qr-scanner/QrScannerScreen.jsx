import { useEffect, useRef, useState } from "react";
import { View, Text, Pressable, Alert, Linking, AppState, StyleSheet } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useIsFocused } from "@react-navigation/native";
import { Ionicons } from "@expo/vector-icons";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";
import AuthButton from "../../../components/auth/AuthButton.jsx";
import { api } from "../../../services/appApi.js";
import styles from "../../../styles/customerStyles.js";

export default function QrScannerScreen({ navigation }) {
  const [permission, requestPermission, getPermission] = useCameraPermissions();
  const [torch, setTorch] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [appActive, setAppActive] = useState(
    AppState.currentState === "active",
  );
  const [paused, setPaused] = useState(false);
  const isFocused = useIsFocused();
  // Ref chặn ngay callback liên tiếp, không phải chờ React cập nhật state.
  const scanLocked = useRef(false);

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (state) => {
      setAppActive(state === "active");
      // Đọc lại quyền khi quay về từ Cài đặt hệ thống.
      if (state === "active")
        getPermission().catch(() =>
          setCameraError("Không đọc được quyền camera."),
        );
    });
    return () => subscription.remove();
  }, [getPermission]);

  function resumeScan() {
    scanLocked.current = false;
    setPaused(false);
  }

  async function handleScanned({ data }) {
    if (scanLocked.current) return;
    scanLocked.current = true; setPaused(true);
    try {
      const result = await api('/qr/scan', { method: 'POST', body: { content: data } });
      navigation.replace('ProductDetail', { productId: result.product.id });
    } catch (error) {
      Alert.alert('Không mở được sản phẩm', error.message, [{ text: 'Quét lại', onPress: resumeScan }], { cancelable: false });
    }
  }

  async function allowCamera() {
    setCameraError("");
    try {
      if (permission?.canAskAgain === false) await Linking.openSettings();
      else await requestPermission();
    } catch {
      setCameraError(
        "Không mở được quyền camera. Hãy kiểm tra trong cài đặt thiết bị.",
      );
    }
  }

  if (!permission)
    return (
      <CustomerPage title="Quét QR" navigation={navigation}>
        <Text style={styles.text}>Đang kiểm tra quyền camera…</Text>
      </CustomerPage>
    );

  if (!permission.granted || cameraError) {
    return (
      <CustomerPage title="Quét QR" navigation={navigation}>
        <View style={styles.empty}>
          <Ionicons name="camera-outline" size={60} color="#777" />
          <Text style={[styles.text, styles.centerText]}>
            {cameraError || "Cho phép dùng camera để quét mã QR trên sản phẩm."}
          </Text>
          <AuthButton
            title={
              cameraError && permission.granted
                ? "Thử lại camera"
                : permission.canAskAgain
                  ? "Cho phép camera"
                  : "Mở cài đặt"
            }
            onPress={
              cameraError && permission.granted
                ? () => setCameraError("")
                : allowCamera
            }
          />
          <AuthButton
            title="Xem sản phẩm"
            onPress={() =>
              navigation.navigate("Home")
            }
          />
        </View>
      </CustomerPage>
    );
  }

  return (
    <CustomerPage
      title="Quét QR sản phẩm"
      navigation={navigation}
      scroll={false}
      rightElement={
        <Pressable
          style={styles.iconButton}
          onPress={() => setTorch(!torch)}
          accessibilityRole="button"
          accessibilityLabel={torch ? "Tắt đèn pin" : "Bật đèn pin"}
        >
          <Ionicons
            name={torch ? "flash" : "flash-outline"}
            size={23}
            color="#111"
          />
        </Pressable>
      }
    >
      <View style={scannerStyles.frame}>
        {/* Camera chỉ hoạt động khi màn này đang được xem và app ở foreground. */}
        {isFocused && appActive && (
          <CameraView
            style={scannerStyles.fill}
            facing="back"
            enableTorch={torch}
            barcodeScannerSettings={{ barcodeTypes: ["qr"] }}
            onBarcodeScanned={paused ? undefined : handleScanned}
            onMountError={() =>
              setCameraError("Không khởi động được camera. Vui lòng thử lại.")
            }
          />
        )}
        <View style={scannerStyles.overlay} pointerEvents="none">
          <View style={scannerStyles.box} />
          <Text style={scannerStyles.hint}>Đặt mã QR trước camera</Text>
        </View>
      </View>
      <View style={styles.cameraActions}>
        <Text style={[styles.muted, styles.centerText]}>
          Quét mã UUID hoặc VFIT:mã-sản-phẩm của cửa hàng.
        </Text>
        <AuthButton
          title="Xem sản phẩm"
          onPress={() =>
            navigation.navigate("Home")
          }
        />
      </View>
    </CustomerPage>
  );
}

// Camera và lớp khung cùng phủ một vùng cha, không chia chiều cao thành hai phần.
const scannerStyles = StyleSheet.create({
  frame: { flex: 1, position: 'relative', overflow: 'hidden', backgroundColor: '#111' },
  fill: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0 },
  overlay: { position: 'absolute', top: 0, right: 0, bottom: 0, left: 0, alignItems: 'center', justifyContent: 'center' },
  box: { width: '70%', maxWidth: 280, aspectRatio: 1, borderWidth: 2, borderColor: '#fff', borderRadius: 12 },
  hint: { position: 'absolute', bottom: 16, left: 16, right: 16, color: '#fff', textAlign: 'center', backgroundColor: '#0009', padding: 12 },
});
