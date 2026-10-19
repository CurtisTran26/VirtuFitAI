import { Text } from "react-native";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";

export default function FeaturePendingScreen({ navigation, route }) {
  const search = route.params?.feature === "Search";
  return (
    <CustomerPage
      title={route.params?.title || "Tính năng đang phát triển"}
      navigation={navigation}
    >
      <Text style={{ fontSize: 16, lineHeight: 25 }}>
        {search
          ? "Tìm kiếm và lọc sản phẩm do Lộc thực hiện. Màn hình này sẽ được thay bằng giao diện của Lộc khi gộp code."
          : "Chức năng này đang được phát triển. Bạn có thể quay lại Trang chủ để tiếp tục xem sản phẩm."}
      </Text>
    </CustomerPage>
  );
}
