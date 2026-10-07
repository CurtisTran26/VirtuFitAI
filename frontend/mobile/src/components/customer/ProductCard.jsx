import { View, Text, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ProductImage from './ProductImage.jsx';
import { useMobileSession } from '../../context/MobileSessionContext.jsx';
import { formatPrice } from '../../data/demoProducts.js';
import styles from '../../styles/customerStyles.js';

export default function ProductCard({ product, onOpen }) {
  const { customerData, toggleWishlist } = useMobileSession();
  const selected = customerData.wishlist.includes(product.id);
  return (
    <View style={styles.card}>
      <Pressable onPress={onOpen} accessibilityRole="button" accessibilityLabel={`Xem ${product.name}`}>
        <ProductImage product={product} />
        <Text style={styles.productName} numberOfLines={2}>{product.name}</Text>
        <Text style={styles.productPrice}>{formatPrice(product.price)}</Text>
        <Text style={styles.muted}>Đã bán {product.sold}</Text>
      </Pressable>
      <Pressable style={styles.heart} onPress={() => toggleWishlist(product.id)} accessibilityRole="button"
        accessibilityLabel={selected ? `Bỏ yêu thích ${product.name}` : `Yêu thích ${product.name}`} accessibilityState={{ selected }}>
        <Ionicons name={selected ? 'heart' : 'heart-outline'} size={23} color={selected ? '#c9362b' : '#111'} />
      </Pressable>
    </View>
  );
}
