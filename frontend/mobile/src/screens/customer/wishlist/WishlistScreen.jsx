import { View, Text, FlatList } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";
import ProductCard from "../../../components/customer/ProductCard.jsx";
import AuthButton from "../../../components/auth/AuthButton.jsx";
import { useMobileSession } from "../../../context/MobileSessionContext.jsx";
import styles from "../../../styles/customerStyles.js";

export default function WishlistScreen({ navigation }) {
  const { customerData } = useMobileSession();
  const products = customerData.wishlistProducts;
  return (
    <CustomerPage title="Yêu thích" navigation={navigation} scroll={false}>
      <FlatList
        data={products}
        numColumns={2}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.content}
        columnWrapperStyle={styles.gridRow}
        ListHeaderComponent={
          products.length > 0 ? (
            <Text style={[styles.muted, { marginBottom: 16 }]}>
              {products.length} sản phẩm yêu thích
            </Text>
          ) : null
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="heart-outline" size={55} color="#999" />
            <Text style={styles.title}>Chưa có sản phẩm yêu thích</Text>
            <Text style={[styles.muted, styles.centerText]}>
              Bấm biểu tượng trái tim tại sản phẩm để lưu vào đây.
            </Text>
            <AuthButton
              title="Xem sản phẩm"
              onPress={() => navigation.navigate("Home")}
            />
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
    </CustomerPage>
  );
}
