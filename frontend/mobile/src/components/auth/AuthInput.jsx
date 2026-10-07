import { useState } from 'react';
import { View, Text, TextInput, Pressable } from 'react-native';
import styles from '../../styles/authStyles.js';

export default function AuthInput({ label, password = false, rightElement, ...inputProps }) {
  const [visible, setVisible] = useState(false);
  return (
    <View style={styles.fieldBlock}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={styles.field}>
        <TextInput {...inputProps} accessibilityLabel={label || inputProps.placeholder}
          style={styles.input} placeholderTextColor="#888"
          autoCapitalize="none" autoCorrect={false} secureTextEntry={password && !visible} />
        {password && (
          <Pressable onPress={() => setVisible(!visible)} style={styles.fieldAction}
            accessibilityRole="button" accessibilityLabel={visible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}>
            <Text style={styles.actionText}>{visible ? 'Ẩn' : 'Hiện'}</Text>
          </Pressable>
        )}
        {rightElement}
      </View>
    </View>
  );
}
