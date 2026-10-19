import { Text } from "react-native";
import AuthLayout from "../../../components/auth/AuthLayout.jsx";
import AuthButton from "../../../components/auth/AuthButton.jsx";
import styles from "../../../styles/authStyles.js";

// Trang kiểm tra luồng đăng nhập, sẽ thay bằng trang chủ khách hàng của nhóm.
export default function AuthDemoScreen({ navigation, route }) {
  return (
    <AuthLayout title="Đăng nhập thử thành công">
      <Text style={styles.subtitle}>
        Tài khoản: {route.params.phone}
        {"\n"}Đây là màn kiểm tra điều hướng. Trang chủ sẽ được ghép vào sau.
      </Text>
      <AuthButton
        title="Đăng xuất"
        onPress={() =>
          navigation.reset({ index: 0, routes: [{ name: "Login" }] })
        }
      />
    </AuthLayout>
  );
}
