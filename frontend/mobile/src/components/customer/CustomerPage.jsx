import { View, Text, Pressable, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import styles from '../../styles/customerStyles.js';

// scroll=false dành cho màn đã có FlatList hoặc camera, tránh lồng hai vùng cuộn.
export default function CustomerPage({ title, navigation, children, scroll = true, rightElement, footer }) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <Pressable style={styles.iconButton} onPress={() => navigation.goBack()} accessibilityRole="button" accessibilityLabel="Quay lại">
          <Ionicons name="arrow-back" size={24} color="#111" />
        </Pressable>
        <Text style={styles.headerTitle}>{title}</Text>
        {rightElement || <View style={styles.iconButton} />}
      </View>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        {scroll ? <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">{children}</ScrollView> : children}
        {footer}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
