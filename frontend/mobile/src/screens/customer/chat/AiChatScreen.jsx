import { Text, View } from 'react-native';
import CustomerPage from '../../../components/customer/CustomerPage.jsx';
import AuthButton from '../../../components/auth/AuthButton.jsx';
import styles from '../../../styles/customerStyles.js';

export default function AiChatScreen({ navigation }) {
  return (
    <CustomerPage title="Trợ lý AI" navigation={navigation}>
      <View style={styles.empty}>
        <Text style={[styles.text, styles.centerText]}>Trợ lý AI tạm thời chưa khả dụng. Bạn có thể tìm trang phục trong danh mục sản phẩm.</Text>
        <AuthButton title="Tìm sản phẩm" onPress={() => navigation.navigate('Search')} />
      </View>
    </CustomerPage>
  );
}
