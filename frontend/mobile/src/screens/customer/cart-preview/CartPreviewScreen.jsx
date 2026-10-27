import { View, Text } from 'react-native';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
import { formatPrice } from '../../../services/appApi.js';
import { useMobileSession } from '../../../context/MobileSessionContext.jsx';
import styles from '../../../styles/customerStyles.js';

// Chỉ kiểm tra dữ liệu từ nút Thêm vào giỏ. Không phải chức năng checkout PB21/22.
export default function CartPreviewScreen({ navigation }) {
  const { customerData } = useMobileSession();
  const rows = customerData.cart;
  const total = rows.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  return (
    <CustomerPage title="Giỏ hàng" navigation={navigation}>
      <View style={styles.note}><Text style={styles.muted}>Các sản phẩm đã chọn chưa được đặt hàng. Thanh toán tạm thời chưa khả dụng.</Text></View>
      {rows.length === 0 && <Text style={styles.text}>Chưa có sản phẩm trong giỏ hàng.</Text>}
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
