import { useEffect, useState } from 'react';
import { sendOtp } from '../services/authApiService.js';

// Dùng chung cho đăng ký và quên mật khẩu; OTP gắn với số đã gửi.
export default function usePhoneOtp(purpose, initialPhone = '') {
  const [phone, setPhone] = useState(initialPhone);
  const [code, setCode] = useState('');
  const [request, setRequest] = useState(null);
  const [now, setNow] = useState(Date.now());
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Tính từ mốc thời gian thực để không đếm sai khi app chạy nền.
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  function changePhone(value) {
    setPhone(value.replace(/\D/g, '').slice(0, 10));
    setCode('');
    setRequest(null);
    setError('');
  }

  async function requestCode() {
    setError('');
    setSending(true);
    try {
      const result = await sendOtp(phone, purpose);
      setRequest(result);
      setNow(Date.now());
      setCode('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  return {
    phone, changePhone, code,
    changeCode: (value) => setCode(value.replace(/\D/g, '').slice(0, 6)),
    debugCode: request?.debugCode, requestCode, sending, error, hasSent: request !== null,
    resendSeconds: request ? Math.max(0, Math.ceil((request.resendAt - now) / 1000)) : 0,
    expiresSeconds: request ? Math.max(0, Math.ceil((request.expiresAt - now) / 1000)) : 0,
  };
}
