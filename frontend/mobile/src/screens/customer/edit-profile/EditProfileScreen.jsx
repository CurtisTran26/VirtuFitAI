import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  Image,
  Alert,
  Linking,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import CustomerPage from "../../../components/customer/CustomerPage.jsx";
import AuthButton from "../../../components/auth/AuthButton.jsx";
import { useMobileSession } from "../../../context/MobileSessionContext.jsx";
import styles from "../../../styles/customerStyles.js";

export default function EditProfileScreen({ navigation }) {
  const { customerData, saveProfile } = useMobileSession();
  // Chỉnh bản nháp: bấm Quay lại mà chưa Lưu thì hồ sơ cũ vẫn được giữ.
  const [draft, setDraft] = useState({ ...customerData.profile });
  const [error, setError] = useState("");
  const [picking, setPicking] = useState(false);
  const [saving, setSaving] = useState(false);

  function change(field, value) {
    setDraft((current) => ({ ...current, [field]: value }));
    setError("");
  }

  async function chooseAvatar() {
    setPicking(true);
    setError("");
    try {
      const permission =
        await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        Alert.alert(
          "Quyền chọn ảnh",
          "Cho phép truy cập ảnh để chọn ảnh đại diện.",
          [
            { text: "Đóng", style: "cancel" },
            {
              text: "Mở cài đặt",
              onPress: () =>
                Linking.openSettings().catch(() =>
                  setError("Không mở được cài đặt."),
                ),
            },
          ],
        );
        return;
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.6,
        base64: true,
      });
      if (!result.canceled && result.assets?.[0]) {
        const asset = result.assets[0];
        if (!asset.base64 || asset.base64.length > 2796204) throw new Error('Vui lòng chọn ảnh nhỏ hơn 2 MB.');
        setDraft(current => ({ ...current, avatarUri: asset.uri, avatarData: `data:image/jpeg;base64,${asset.base64}` }));
      }
    } catch (err) {
      setError(err.message || "Không mở được thư viện ảnh. Vui lòng thử lại.");
    } finally {
      setPicking(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      await saveProfile(draft);
      Alert.alert("Đã lưu", "Hồ sơ đã được lưu trên máy chủ.", [
        { text: "Đóng", onPress: () => navigation.goBack() },
      ]);
    } catch (err) {
      setError(err.message);
    } finally { setSaving(false); }
  }

  const fields = [
    {
      key: "name",
      label: "Họ và tên",
      placeholder: "Nhập họ và tên",
      maxLength: 80,
    },
    { key: "phone", label: "Số điện thoại", readOnly: true },
    {
      key: "birthday",
      label: "Ngày sinh",
      placeholder: "dd/mm/yyyy",
      maxLength: 10,
    },
    {
      key: "email",
      label: "Email đăng nhập Google",
      placeholder: "Chưa liên kết Google",
      readOnly: true,
    },
    {
      key: "height",
      label: "Chiều cao (cm)",
      placeholder: "Ví dụ: 170",
      keyboard: "decimal-pad",
      maxLength: 5,
    },
    {
      key: "weight",
      label: "Cân nặng (kg)",
      placeholder: "Ví dụ: 65",
      keyboard: "decimal-pad",
      maxLength: 5,
    },
  ];

  return (
    <CustomerPage title="Hồ sơ cá nhân" navigation={navigation}>
      <View style={styles.avatarFrame}>
        {draft.avatarUri ? (
          <Image source={{ uri: draft.avatarUri }} style={styles.avatar} />
        ) : (
          <Ionicons name="person-circle-outline" size={100} color="#111" />
        )}
        <Pressable
          style={styles.editPhoto}
          onPress={chooseAvatar}
          disabled={picking || saving}
          accessibilityRole="button"
          accessibilityLabel="Chọn ảnh đại diện"
        >
          <Ionicons name="camera-outline" size={23} color="#111" />
        </Pressable>
      </View>
      {fields.map((field) => (
        <View key={field.key} style={styles.fieldGroup}>
          <Text style={styles.label}>{field.label}</Text>
          <TextInput
            style={[styles.input, field.readOnly && styles.readOnly]}
            value={draft[field.key]}
            onChangeText={(value) =>
              change(
                field.key,
                field.keyboard ? value.replace(",", ".") : value,
              )
            }
            editable={!field.readOnly && !saving}
            placeholder={field.placeholder}
            placeholderTextColor="#888"
            accessibilityLabel={field.label}
            keyboardType={field.keyboard || "default"}
            maxLength={field.maxLength}
          />
        </View>
      ))}
      <Text style={styles.muted}>
        Số điện thoại và email đăng nhập cần xác minh riêng nên không sửa tại
        đây. Chiều cao, cân nặng là thông tin tùy chọn.
      </Text>
      {error !== "" && (
        <Text style={styles.error} accessibilityLiveRegion="polite">
          {error}
        </Text>
      )}
      <View style={{ marginTop: 24 }}>
        <AuthButton
          title="Lưu thay đổi"
          loading={saving}
          onPress={handleSave}
          disabled={picking || saving}
        />
      </View>
    </CustomerPage>
  );
}
