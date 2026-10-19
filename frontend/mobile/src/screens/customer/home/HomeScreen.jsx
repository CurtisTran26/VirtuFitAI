import { useState } from "react";
import {
  FlatList,
  Image,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { demoProducts, formatPrice } from "../../../data/demoProducts.js";
import FloatingAiButton from "../../../components/customer/FloatingAiButton.jsx";

const shortcuts = [
  { label: "Sản phẩm", icon: "shirt-outline", target: "Search" },
  { label: "Quét QR", icon: "qr-code-outline", target: "QrScanner" },
  { label: "Danh mục", icon: "grid-outline", target: "Search" },
  { label: "Yêu thích", icon: "heart-outline", target: "Wishlist" },
  { label: "Thử đồ AI", icon: "sparkles-outline", target: "TryOn" },
];
const tabs = [
  {
    label: "Thông báo",
    icon: "notifications-outline",
    target: "Notifications",
  },
  { label: "Quét QR", icon: "qr-code-outline", target: "QrScanner" },
  { label: "Trang chủ", icon: "home-outline", target: "Home" },
  { label: "Thiết kế", icon: "color-wand-outline", target: "CustomDesign" },
  { label: "Tài khoản", icon: "person-circle-outline", target: "Profile" },
];

export default function HomeScreen({ navigation }) {
  const [area, setArea] = useState({ width: 0, height: 0 });

  // Các màn của Lộc / sprint sau có màn chờ rõ ràng. Thay bằng màn thật khi gộp code.
  function openScreen(target, title) {
    if (target === "Home") return;
    if (
      [
        "Search",
        "Notifications",
        "CustomDesign",
        "TryOn",
        "SupportChat",
      ].includes(target)
    ) {
      navigation.navigate("FeaturePending", { feature: target, title });
      return;
    }
    navigation.navigate(target);
  }

  function renderProduct({ item }) {
    return (
      <Pressable
        style={styles.card}
        onPress={() =>
          navigation.navigate("ProductDetail", { productId: item.id })
        }
        accessibilityRole="button"
        accessibilityLabel={`${item.name}, ${formatPrice(item.price)}`}
      >
        {item.imageSource ? (
          <Image
            source={item.imageSource}
            style={styles.productImage}
            resizeMode="cover"
          />
        ) : (
          <View style={[styles.productImage, styles.imagePlaceholder]}>
            <Ionicons name="shirt-outline" size={52} color="#aaa" />
            <Text style={styles.placeholderText}>Chưa có ảnh</Text>
          </View>
        )}
        <View style={styles.cardInfo}>
          <Text numberOfLines={2} style={styles.productName}>
            {item.name}
          </Text>
          <Text style={styles.price}>{formatPrice(item.price)}</Text>
          <Text style={styles.sold}>Đã bán {item.sold}</Text>
        </View>
      </Pressable>
    );
  }

  return (
    <SafeAreaView
      style={styles.page}
      edges={["top", "bottom", "left", "right"]}
    >
      <View style={styles.header}>
        <Pressable
          style={styles.search}
          onPress={() => openScreen("Search", "Tìm kiếm và lọc sản phẩm")}
          accessibilityRole="button"
          accessibilityLabel="Tìm kiếm sản phẩm"
        >
          <Text style={styles.searchHint}>Tìm kiếm</Text>
          <Ionicons name="search-outline" size={22} />
        </Pressable>
        <Pressable
          style={styles.iconButton}
          onPress={() => navigation.navigate("CartPreview")}
          accessibilityRole="button"
          accessibilityLabel="Giỏ hàng"
        >
          <Ionicons name="cart-outline" size={27} />
        </Pressable>
        <Pressable
          style={styles.iconButton}
          onPress={() => openScreen("SupportChat", "Chat với nhân viên")}
          accessibilityRole="button"
          accessibilityLabel="Chat với nhân viên"
        >
          <Ionicons name="chatbubbles-outline" size={25} />
        </Pressable>
      </View>

      <View
        style={styles.content}
        onLayout={(event) => setArea(event.nativeEvent.layout)}
      >
        <FlatList
          data={demoProducts}
          keyExtractor={(item) => item.id}
          numColumns={2}
          renderItem={renderProduct}
          contentContainerStyle={styles.list}
          columnWrapperStyle={styles.row}
          ListHeaderComponent={
            <View>
              <View style={styles.shortcuts}>
                {shortcuts.map((item) => (
                  <Pressable
                    key={item.label}
                    style={styles.shortcut}
                    onPress={() => openScreen(item.target, item.label)}
                    accessibilityRole="button"
                  >
                    <Ionicons name={item.icon} size={27} />
                    <Text style={styles.shortcutText}>{item.label}</Text>
                  </Pressable>
                ))}
              </View>
              <Text style={styles.demoNote}>
                Sản phẩm minh họa · Chưa kết nối cửa hàng
              </Text>
            </View>
          }
        />
        <FloatingAiButton
          width={area.width}
          height={area.height}
          onPress={() => navigation.navigate("AiChat")}
        />
      </View>

      <View style={styles.tabs}>
        {tabs.map((item) => (
          <Pressable
            key={item.target}
            style={styles.tab}
            onPress={() => openScreen(item.target, item.label)}
            accessibilityRole="button"
            accessibilityState={{ selected: item.target === "Home" }}
          >
            <Ionicons
              name={item.icon}
              size={24}
              color={item.target === "Home" ? "#111" : "#555"}
            />
            <Text
              style={[
                styles.tabText,
                item.target === "Home" && styles.activeTab,
              ]}
            >
              {item.label}
            </Text>
          </Pressable>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: "#fff" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 10,
    gap: 6,
  },
  search: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: "#999",
    borderRadius: 5,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 10,
  },
  searchHint: { color: "#888", fontSize: 13 },
  iconButton: {
    width: 42,
    height: 44,
    justifyContent: "center",
    alignItems: "center",
  },
  content: { flex: 1 },
  list: { paddingHorizontal: 16, paddingBottom: 88 },
  shortcuts: { flexDirection: "row", paddingTop: 8, paddingBottom: 18 },
  shortcut: { flex: 1, alignItems: "center", minHeight: 52, gap: 5 },
  shortcutText: { fontSize: 10, textAlign: "center", color: "#222" },
  demoNote: { fontSize: 11, color: "#777", marginBottom: 10 },
  row: { justifyContent: "space-between" },
  card: { width: "48%", marginBottom: 16, backgroundColor: "#f1f1f1" },
  productImage: { width: "100%", aspectRatio: 0.82 },
  imagePlaceholder: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#e7e7e7",
  },
  placeholderText: { fontSize: 11, color: "#777", marginTop: 6 },
  cardInfo: { padding: 8 },
  productName: { fontSize: 13, minHeight: 32 },
  price: { fontSize: 14, color: "#ef3038", fontWeight: "600", marginTop: 4 },
  sold: { fontSize: 10, marginTop: 12, color: "#444" },
  tabs: {
    flexDirection: "row",
    borderTopWidth: 1,
    borderColor: "#eee",
    paddingTop: 9,
    paddingBottom: 4,
  },
  tab: {
    flex: 1,
    minHeight: 48,
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
  },
  tabText: { fontSize: 10, color: "#777" },
  activeTab: { color: "#111", fontWeight: "700" },
});
