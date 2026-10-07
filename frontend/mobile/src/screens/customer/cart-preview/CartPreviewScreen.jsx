import { View, Text } from 'react-native';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
import { getProductById, formatPrice } from '../../../data/demoProducts.js';
import { useMobileSession } from '../../../context/MobileSessionContext.jsx';
import styles from '../../../styles/customerStyles.js';

// Chỉ kiểm tra dữ liệu từ nút Thêm vào giỏ. Không phải chức năng checkout PB21/22.
export default function CartPreviewScreen({ navigation }) {
  const { customerData } = useMobileSession();
  const rows = customerData.cart.map((item) => {
    const product = getProductById(item.productId);
    return { ...item, product, variant: product.variants.find((variant) => variant.id === item.variantId) };
  });
  const total = rows.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  return (
    <CustomerPage title="Giỏ thử nghiệm" navigation={navigation}>
      <View style={styles.note}><Text style={styles.muted}>Màn kiểm tra lựa chọn sản phẩm của Sprint 1. Chưa đặt đơn, thanh toán hoặc giữ tồn kho thật.</Text></View>
      {rows.length === 0 && <Text style={styles.text}>Chưa có sản phẩm trong giỏ thử.</Text>}
      {rows.map((item) => (
        <View key={item.variantId} style={{ marginBottom: 20 }}>
          <Text style={styles.section}>{item.product.name}</Text>
          <Text style={styles.text}>{item.variant.color} · {item.variant.size} · Số lượng {item.quantity}</Text>
          <Text style={styles.productPrice}>{formatPrice(item.product.price * item.quantity)}</Text>
        </View>
      ))}
      <Text style={styles.section}>Tạm tính: {formatPrice(total)}</Text>
    </CustomerPage>
  );
}
