import { useEffect, useMemo, useRef, useState } from 'react';
import { PanResponder, StyleSheet, Text, View } from 'react-native';

const SIZE = 62;
const GAP = 8;

// Giữ nút bên trong vùng nội dung, không đè lên thanh điều hướng phía dưới.
export function clampPosition(position, width, height) {
  return {
    x: Math.max(GAP, Math.min(position.x, Math.max(GAP, width - SIZE - GAP))),
    y: Math.max(GAP, Math.min(position.y, Math.max(GAP, height - SIZE - GAP))),
  };
}

export default function FloatingAiButton({ width, height, onPress }) {
  const [position, setPosition] = useState({ x: GAP, y: GAP });
  const current = useRef(position);
  const start = useRef(position);
  const initialized = useRef(false);
  const moved = useRef(false);
  const openChat = useRef(onPress);
  openChat.current = onPress;

  function updatePosition(next) {
    current.current = next;
    setPosition(next);
  }

  useEffect(() => {
    if (!width || !height) return;
    const next = initialized.current ? current.current : { x: width - SIZE - GAP, y: height - SIZE - 20 };
    updatePosition(clampPosition(next, width, height));
    initialized.current = true;
  }, [width, height]);

  const responder = useMemo(() => PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: () => true,
    onPanResponderGrant: () => {
      start.current = current.current;
      moved.current = false;
    },
    onPanResponderMove: (_, gesture) => {
      // Di chuyển quá 8 điểm là kéo. Kéo xong không tự mở chat.
      if (Math.abs(gesture.dx) > 8 || Math.abs(gesture.dy) > 8) moved.current = true;
      if (moved.current) {
        updatePosition(clampPosition({ x: start.current.x + gesture.dx, y: start.current.y + gesture.dy }, width, height));
      }
    },
    onPanResponderRelease: () => { if (!moved.current) openChat.current(); },
    onPanResponderTerminationRequest: () => false,
    onPanResponderTerminate: () => { moved.current = false; },
  }), [width, height]);

  if (!width || !height) return null;
  return (
    <View {...responder.panHandlers} style={[styles.button, { left: position.x, top: position.y }]}
      accessible accessibilityRole="button" accessibilityLabel="Mở trò chuyện với AI"
      accessibilityHint="Chạm để mở chat. Có thể kéo nút đến vị trí khác."
      onAccessibilityTap={() => openChat.current()}>
      <View style={styles.antenna} />
      <View style={styles.robot}><View style={styles.eye} /><View style={styles.eye} /></View>
      <Text style={styles.label}>AI</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  button: { position: 'absolute', width: SIZE, height: SIZE, zIndex: 10, elevation: 5, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff', borderRadius: 18, borderWidth: 1, borderColor: '#ddd', shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } },
  antenna: { width: 3, height: 7, backgroundColor: '#222' },
  robot: { width: 36, height: 24, borderWidth: 2, borderColor: '#222', borderRadius: 7, flexDirection: 'row', justifyContent: 'space-evenly', alignItems: 'center' },
  eye: { width: 6, height: 7, borderRadius: 3, backgroundColor: '#222' },
  label: { fontSize: 10, fontWeight: '700', marginTop: 2 },
});
