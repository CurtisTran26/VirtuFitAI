import { Text } from 'react-native';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
export default function FeaturePendingScreen({ navigation, route }) {
  return <CustomerPage title={route.params?.title || 'Thông báo'} navigation={navigation}>
    <Text style={{ fontSize: 16, lineHeight: 25 }}>Chức năng này tạm thời chưa khả dụng. Bạn có thể quay lại Trang chủ để tiếp tục xem sản phẩm.</Text>
  </CustomerPage>;

}
