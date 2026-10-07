import { useState } from 'react';
import { Image, View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import styles from '../../styles/customerStyles.js';

export default function ProductImage({ product }) {
  const [failed, setFailed] = useState(false);
  if (product.imageSource && !failed) {
    return <Image source={product.imageSource} style={styles.productImage} resizeMode="contain" onError={() => setFailed(true)} accessibilityLabel={product.name} />;
  }
  return (
    <View style={[styles.productImage, styles.placeholder]}>
      <Ionicons name="image-outline" size={42} color="#999" />
      <Text style={styles.productPlaceholderLabel}>Chưa có ảnh sản phẩm</Text>
    </View>
  );
}
