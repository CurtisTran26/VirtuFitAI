import { useEffect, useState } from "react";
import { View, Text, Pressable, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";
import ProductImage from "../../../components/customer/ProductImage.jsx";
import AuthButton from "../../../components/auth/AuthButton.jsx";
import {
  getVariant,
  formatPrice,
} from "../../../services/appApi.js";
import { useMobileSession } from "../../../context/MobileSessionContext.jsx";
import styles from "../../../styles/customerStyles.js";

export default function ProductDetailScreen({ navigation, route }) {
  const { customerData, toggleWishlist, addToCart, loadProduct } = useMobileSession();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  const [color, setColor] = useState("");
  const [size, setSize] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true; setLoading(true); setProduct(null); setError('');
    setColor(''); setSize(''); setQuantity(1);
    loadProduct(route.params?.productId).then(value => { if (active) setProduct(value); })
      .catch(err => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [route.params?.productId]);
  async function handleWishlist() {
    setWishlistLoading(true); setError('');
    try { await toggleWishlist(product.id); } catch (err) { setError(err.message); }
    finally { setWishlistLoading(false); }
  }
  if (!product) {
    return (
      <CustomerPage title="Sản phẩm" navigation={navigation}>
        <Text style={styles.error}>
          {loading ? "Đang tải sản phẩm…" : error || "Không tìm thấy sản phẩm."}
        </Text>
      </CustomerPage>
    );
  }
  const selected = customerData.wishlist.includes(product.id);
  const variant = getVariant(product, color, size);
  const totalStock = product.variants.reduce(
    (sum, item) => sum + item.stock,
    0,
  );

  function chooseColor(value) {
    setColor(value);
    // Size cũ có thể không còn hàng ở màu mới, yêu cầu chọn lại để tránh nhầm.
    setSize("");
    setQuantity(1);
    setError("");
  }

  function handleAddToCart() {
    setError("");
    try {
      addToCart(product.id, variant?.id, quantity);
      Alert.alert(
        "Đã thêm vào giỏ thử",
        `${quantity} ${product.name} — ${color}, ${size}`,
        [
          { text: "Tiếp tục xem", style: "cancel" },
          {
            text: "Xem giỏ thử",
            onPress: () => navigation.navigate("CartPreview"),
          },
        ],
      );
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <CustomerPage
      title="Chi tiết sản phẩm"
      navigation={navigation}
      rightElement={
        <Pressable
          style={styles.iconButton}
          onPress={() => navigation.navigate("CartPreview")}
          accessibilityRole="button"
          accessibilityLabel="Giỏ thử nghiệm"
        >
          <Ionicons name="cart-outline" size={25} color="#111" />
        </Pressable>
      }
      footer={
        <View style={styles.bottomBar}>
          <Text style={[styles.muted, styles.centerText]}>
            Tổng: {formatPrice(product.price * quantity)}
          </Text>
          <AuthButton
            title={
              totalStock === 0 ? "Sản phẩm đã hết hàng" : "Thêm vào giỏ thử"
            }
            onPress={handleAddToCart}
            disabled={totalStock === 0 || !variant || variant.stock === 0}
          />
        </View>
      }
    >
      <ProductImage product={product} />
      <View style={[styles.between, { marginTop: 24 }]}>
        <Text style={styles.price}>{formatPrice(product.price)}</Text>
        <Pressable
          onPress={handleWishlist}
          disabled={wishlistLoading}
          style={styles.iconButton}
          accessibilityRole="button"
          accessibilityLabel={selected ? "Bỏ yêu thích" : "Thêm yêu thích"}
          accessibilityState={{ selected }}
        >
          <Ionicons
            name={selected ? "heart" : "heart-outline"}
            size={28}
            color={selected ? "#c9362b" : "#111"}
          />
        </Pressable>
      </View>
      <Text style={styles.title}>{product.name}</Text>
      <Text style={styles.muted}>
        Mã {product.sku} · Còn {totalStock} sản phẩm
      </Text>
      <Text style={styles.section}>Mô tả</Text>
      <Text style={styles.text}>{product.description}</Text>
      <Text style={styles.section}>Màu sắc</Text>
      <View style={styles.chips}>
        {product.colors.map((value) => (
          <Pressable
            key={value}
            onPress={() => chooseColor(value)}
            style={[styles.chip, color === value && styles.selectedChip]}
            accessibilityRole="button"
            accessibilityState={{ selected: color === value }}
          >
            <Text
              style={[styles.chipText, color === value && styles.selectedText]}
            >
              {value}
            </Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.section}>Kích thước</Text>
      {!color && (
        <Text style={styles.muted}>Chọn màu trước khi chọn kích thước.</Text>
      )}
      <View style={styles.chips}>
        {product.sizes.map((value) => {
          const candidate = getVariant(product, color, value);
          const available = Boolean(candidate && candidate.stock > 0);
          return (
            <Pressable
              key={value}
              disabled={!available}
              accessibilityRole="button"
              accessibilityLabel={`Size ${value}${available ? "" : ", chưa khả dụng"}`}
              accessibilityState={{
                selected: size === value,
                disabled: !available,
              }}
              onPress={() => {
                setSize(value);
                setQuantity(1);
                setError("");
              }}
              style={[
                styles.chip,
                !available && styles.unavailable,
                size === value && styles.selectedChip,
              ]}
            >
              <Text
                style={[styles.chipText, size === value && styles.selectedText]}
              >
                {value}
              </Text>
            </Pressable>
          );
        })}
      </View>
      <Text style={styles.section}>Số lượng</Text>
      <View style={styles.quantity}>
        <Pressable
          style={styles.iconButton}
          disabled={quantity <= 1}
          onPress={() => setQuantity(quantity - 1)}
          accessibilityRole="button"
          accessibilityLabel="Giảm số lượng"
        >
          <Ionicons
            name="remove"
            size={20}
            color={quantity <= 1 ? "#bbb" : "#111"}
          />
        </Pressable>
        <Text style={styles.quantityText}>{quantity}</Text>
        <Pressable
          style={styles.iconButton}
          disabled={!variant || quantity >= variant.stock}
          onPress={() => setQuantity(quantity + 1)}
          accessibilityRole="button"
          accessibilityLabel="Tăng số lượng"
        >
          <Ionicons
            name="add"
            size={20}
            color={!variant || quantity >= variant.stock ? "#bbb" : "#111"}
          />
        </Pressable>
      </View>
      {variant && (
        <Text style={styles.muted}>
          Biến thể đã chọn còn {variant.stock} sản phẩm.
        </Text>
      )}
      {error !== "" && (
        <Text style={styles.error} accessibilityLiveRegion="polite">
          {error}
        </Text>
      )}
      <View style={{ marginTop: 24 }}>
        <AuthButton
          title="Thử đồ AI"
          onPress={() =>
            Alert.alert(
              "Thử đồ AI",
              "Chức năng này chờ tích hợp AI. Hiện chưa tạo ảnh thử đồ.",
            )
          }
        />
      </View>
    </CustomerPage>
  );
}
