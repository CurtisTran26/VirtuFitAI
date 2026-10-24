import { Text, Pressable, ActivityIndicator } from "react-native";
import AuthInput from "./AuthInput.jsx";
import { formatTime } from "../../utils/authValidation.js";
import styles from "../../styles/authStyles.js";

export default function PhoneOtpFields({
  otp,
  disabled = false,
  phoneEditable = true,
}) {
  const cannotSend = disabled || otp.sending || otp.resendSeconds > 0;
  return (
    <>
      <AuthInput
        label="Số điện thoại"
        placeholder="Nhập số điện thoại"
        value={otp.phone}
        onChangeText={otp.changePhone}
        keyboardType="phone-pad"
        maxLength={10}
        editable={phoneEditable && !disabled && !otp.sending}
        rightElement={
          <Pressable
            onPress={otp.requestCode}
            disabled={cannotSend}
            accessibilityRole="button"
            accessibilityLabel="Gửi mã xác nhận"
            accessibilityState={{ disabled: cannotSend }}
            style={[styles.fieldAction, cannotSend && styles.disabled]}
          >
            {otp.sending ? (
              <ActivityIndicator color="#111" />
            ) : (
              <Text
                style={otp.resendSeconds > 0 ? styles.actionText : styles.plane}
              >
                {otp.resendSeconds > 0 ? `${otp.resendSeconds}s` : "➤"}
              </Text>
            )}
          </Pressable>
        }
      />
      {otp.error !== "" && (
        <Text style={styles.error} accessibilityLiveRegion="polite">
          {otp.error}
        </Text>
      )}
      <AuthInput
        label="Mã xác nhận"
        placeholder="Nhập mã 6 số"
        value={otp.code}
        onChangeText={otp.changeCode}
        keyboardType="number-pad"
        maxLength={6}
        editable={otp.hasSent && !disabled && !otp.sending}
        textContentType="oneTimeCode"
      />
      {otp.hasSent ? (
        <>
          <Text style={styles.hint}>
            {otp.debugCode ? `Mã thử từ server: ${otp.debugCode} • Chưa gửi SMS thật.` : 'Đã gửi yêu cầu SMS. Vui lòng kiểm tra điện thoại.'}
          </Text>
          <Text style={otp.expiresSeconds > 0 ? styles.hint : styles.error}>
            {otp.expiresSeconds > 0
              ? `Mã hết hạn sau ${formatTime(otp.expiresSeconds)}.`
              : "Mã đã hết hạn. Hãy bấm máy bay để gửi lại."}
            {otp.resendSeconds > 0
              ? ` Gửi lại sau ${otp.resendSeconds} giây.`
              : " Có thể gửi lại mã."}
          </Text>
        </>
      ) : (
        <Text style={styles.hint}>
          Bấm nút máy bay bên cạnh số điện thoại để gửi mã.
        </Text>
      )}
    </>
  );
}
