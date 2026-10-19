import { View, Text, FlatList, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import ProductCard from "../../../components/customer/ProductCard.jsx";
import { demoProducts } from "../../../data/demoProducts.js";
import { useMobileSession } from "../../../context/MobileSessionContext.jsx";
import styles from "../../../styles/customerStyles.js";

// Điểm vào để Duy kiểm tra các màn. Khi ghép nhóm, thay màn này bằng Home của Lộc.
export default function SprintPreviewScreen({ navigation }) {
  const { customerData } = useMobileSession();
  const links = [
    ["QrScanner", "qr-code-outline", "Quét QR"],
    ["Wishlist", "heart-outline", "Yêu thích"],
    ["Profile", "person-outline", "Tài khoản"],
  ];
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>VirtuFit AI</Text>
      </View>
      <FlatList
        data={demoProducts}
        keyExtractor={(item) => item.id}
        numColumns={2}
        contentContainerStyle={styles.content}
        columnWrapperStyle={styles.gridRow}
        ListHeaderComponent={
          <View>
            <Text style={styles.title}>
              Xin chào, {customerData.profile.name}
            </Text>
            <View style={styles.note}>
              <Text style={styles.muted}>
                Bộ màn thử Sprint 1 của Duy. Sản phẩm và tài khoản là dữ liệu
                mẫu.
              </Text>
            </View>
            <View style={styles.between}>
              {links.map(([screen, icon, label]) => (
                <Pressable
                  key={screen}
                  style={{ alignItems: "center", padding: 12 }}
                  onPress={() => navigation.navigate(screen)}
                  accessibilityRole="button"
                >
                  <Ionicons name={icon} size={25} color="#111" />
                  <Text style={styles.muted}>{label}</Text>
                </Pressable>
              ))}
            </View>
            <Text style={styles.section}>Sản phẩm để thử chi tiết và QR</Text>
          </View>
        }
        renderItem={({ item }) => (
          <ProductCard
            product={item}
            onOpen={() =>
              navigation.navigate("ProductDetail", { productId: item.id })
            }
          />
        )}
      />
    </SafeAreaView>
  );
}
