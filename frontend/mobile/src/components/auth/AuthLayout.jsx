import { View, Text, Image, Pressable, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import styles from '../../styles/authStyles.js';

export default function AuthLayout({ title, subtitle, onBack, children }) {
  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Cho phép cuộn form khi bàn phím mở hoặc màn hình nhỏ. */}
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
          <View style={styles.page}>
            <View style={styles.topBar}>
              {onBack && (
                <Pressable onPress={onBack} style={styles.back} accessibilityRole="button" accessibilityLabel="Quay lại">
                  <Text style={styles.backText}>←</Text>
                </Pressable>
              )}
            </View>
            <Text style={styles.brand}>VirtuFit AI</Text>
            <View style={styles.artworkFrame}>
              <Image source={require('../../assets/images/fashion-characters.png')} style={styles.artwork} resizeMode="contain" accessibilityLabel="Minh họa thời trang" />
            </View>
            <Text style={styles.title}>{title}</Text>
            {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
            {children}
            <Text style={styles.demo}>Bản thử giao diện • Chưa kết nối máy chủ</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
