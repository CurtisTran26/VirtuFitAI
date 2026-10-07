import { useRef, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { getDemoAiReply } from '../../../services/mockAiChatService.js';

export default function AiChatScreen({ navigation }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { id: 'welcome', role: 'assistant', text: 'Xin chào! Bạn muốn tìm trang phục nào hôm nay?' },
  ]);
  const list = useRef(null);
  const nextId = useRef(1);

  function sendMessage(value = message) {
    const text = value.trim();
    if (!text) return;
    const id = nextId.current++;
    setMessages((previous) => [...previous,
      { id: `user-${id}`, role: 'user', text },
      { id: `reply-${id}`, role: 'assistant', text: getDemoAiReply(text) },
    ]);
    setMessage('');
  }

  return (
    <SafeAreaView style={styles.page}>
      <View style={styles.header}>
        <Pressable onPress={() => navigation.goBack()} style={styles.back} accessibilityRole="button" accessibilityLabel="Quay lại"><Ionicons name="arrow-back" size={24} /></Pressable>
        <View><Text style={styles.title}>Trợ lý AI</Text><Text style={styles.subtitle}>VirtuFit AI</Text></View>
      </View>
      <Text style={styles.notice}>Bản minh họa · Chưa kết nối AI thật · Tin nhắn chưa được lưu</Text>
      <KeyboardAvoidingView style={styles.body} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <FlatList ref={list} data={messages} keyExtractor={(item) => item.id} contentContainerStyle={styles.messages}
          keyboardShouldPersistTaps="handled" onContentSizeChange={() => list.current?.scrollToEnd({ animated: true })}
          renderItem={({ item }) => (
            <View style={[styles.bubble, item.role === 'user' ? styles.userBubble : styles.aiBubble]}>
              <Text style={item.role === 'user' ? styles.userText : styles.aiText}>{item.text}</Text>
            </View>
          )} />
        <View style={styles.suggestions}>{['Giá sản phẩm', 'Chọn size', 'Thử đồ'].map((text) => (
          <Pressable key={text} style={styles.chip} onPress={() => sendMessage(text)} accessibilityRole="button"><Text style={styles.chipText}>{text}</Text></Pressable>
        ))}</View>
        <View style={styles.composer}>
          <TextInput style={styles.input} placeholder="Nhập câu hỏi của bạn..." accessibilityLabel="Nội dung tin nhắn" value={message} onChangeText={setMessage} multiline maxLength={1000} />
          <Pressable style={[styles.send, !message.trim() && styles.disabled]} disabled={!message.trim()} onPress={() => sendMessage()} accessibilityRole="button" accessibilityLabel="Gửi tin nhắn">
            <Ionicons name="paper-plane-outline" size={21} color="#fff" />
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: '#fff' }, body: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', padding: 12, borderBottomWidth: 1, borderColor: '#eee' },
  back: { width: 44, height: 44, justifyContent: 'center' }, title: { fontSize: 18, fontWeight: '700' },
  subtitle: { fontSize: 12, color: '#777', marginTop: 2 },
  notice: { padding: 10, fontSize: 11, color: '#666', backgroundColor: '#f5f5f5' },
  messages: { padding: 16, gap: 12 }, bubble: { maxWidth: '86%', padding: 13, borderRadius: 14 },
  aiBubble: { alignSelf: 'flex-start', backgroundColor: '#f0f0f0' },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#181818' },
  aiText: { color: '#222', lineHeight: 22 }, userText: { color: '#fff', lineHeight: 22 },
  suggestions: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, paddingHorizontal: 12, paddingBottom: 8 },
  chip: { padding: 9, borderWidth: 1, borderColor: '#ddd', borderRadius: 18 }, chipText: { fontSize: 12 },
  composer: { flexDirection: 'row', gap: 8, padding: 12, borderTopWidth: 1, borderColor: '#eee', alignItems: 'flex-end' },
  input: { flex: 1, borderWidth: 1, borderColor: '#ccc', borderRadius: 10, padding: 12, minHeight: 46, maxHeight: 110, textAlignVertical: 'top' },
  send: { width: 46, height: 46, backgroundColor: '#111', borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  disabled: { opacity: 0.35 },
});
