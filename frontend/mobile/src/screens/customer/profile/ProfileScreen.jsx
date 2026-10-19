import { View, Text, Pressable, Image, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";
import { useMobileSession } from "../../../context/MobileSessionContext.jsx";
import styles from "../../../styles/customerStyles.js";

export default function ProfileScreen({ navigation }) {
  const { user, customerData, signOut } = useMobileSession();
  const { profile } = customerData;
  const items = [
    { title: "Hồ sơ cá nhân", icon: "person-outline", screen: "EditProfile" },
    { title: "Địa chỉ", icon: "location-outline" },
    { title: "Đơn hàng", icon: "receipt-outline" },
    { title: "Yêu thích", icon: "heart-outline", screen: "Wishlist" },
    {
      title: "Đổi mật khẩu",
      icon: "lock-closed-outline",
      screen: "ChangePassword",
    },
  ].filter(
    (item) =>
      !(user.authMethod === "google" && item.screen === "ChangePassword"),
  );

  function confirmLogout() {
    Alert.alert("Đăng xuất", "Bạn muốn đăng xuất khỏi tài khoản này?", [
      { text: "Ở lại", style: "cancel" },
      { text: "Đăng xuất", style: "destructive", onPress: signOut },
    ]);
  }

  return (
    <CustomerPage title="Tài khoản" navigation={navigation}>
      <Pressable
        style={styles.profileHeader}
        onPress={() => navigation.navigate("EditProfile")}
        accessibilityRole="button"
        accessibilityLabel="Chỉnh sửa hồ sơ"
      >
        {profile.avatarUri ? (
          <Image
            source={{ uri: profile.avatarUri }}
            style={styles.avatarSmall}
          />
        ) : (
          <Ionicons name="person-circle-outline" size={64} color="#111" />
        )}
        <View style={styles.flex}>
          <Text style={styles.section}>{profile.name}</Text>
          <Text style={styles.muted}>{profile.phone || profile.email}</Text>
        </View>
        <Ionicons name="create-outline" size={24} color="#111" />
      </Pressable>
      {items.map((item) => (
        <Pressable
          key={item.title}
          style={styles.menuRow}
          accessibilityRole="button"
          onPress={() =>
            item.screen
              ? navigation.navigate(item.screen)
              : Alert.alert(
                  item.title,
                  "Phần này sẽ được nối khi nhóm triển khai chức năng tương ứng.",
                )
          }
        >
          <Ionicons name={item.icon} size={22} color="#222" />
          <Text style={styles.menuText}>{item.title}</Text>
          <Ionicons name="chevron-forward" size={18} color="#888" />
        </Pressable>
      ))}
      <Pressable
        style={styles.menuRow}
        onPress={confirmLogout}
        accessibilityRole="button"
      >
        <Ionicons name="log-out-outline" size={22} color="#b42318" />
        <Text style={[styles.menuText, { color: "#b42318" }]}>Đăng xuất</Text>
      </Pressable>
      <Text style={[styles.muted, { marginTop: 24 }]}>
        Hồ sơ và yêu thích chỉ được giữ trong lần chạy thử này.
      </Text>
    </CustomerPage>
  );
}
