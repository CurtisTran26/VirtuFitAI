import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../../utils/apiClient';

const Login = () => {
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [isPasswordVisible, setPasswordVisible] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const result = await apiClient.post('auth/staff-login', { account: account.trim(), password });
      const destinations = { admin: '/admin', warehouse_staff: '/warehouse' };
      const destination = destinations[result.user?.role];

      if (!destination || !result.access_token) {
        throw new Error('Tài khoản này chưa được cấp quyền truy cập web.');
      }

      localStorage.setItem('accessToken', result.access_token);
      localStorage.setItem('userRole', result.user.role);
      localStorage.setItem('userName', result.user.full_name || '');
      navigate(destination);
    } catch (loginError) {
      setError(loginError.message || 'Không thể đăng nhập. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main
      className="flex min-h-screen w-full items-center justify-center px-4 py-8 font-sans text-white sm:px-6"
      style={{
        backgroundColor: '#0b0f18',
        backgroundImage: 'linear-gradient(rgba(148, 163, 184, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(148, 163, 184, 0.035) 1px, transparent 1px)',
        backgroundSize: '44px 44px',
      }}
    >
      <div className="grid w-full max-w-5xl overflow-hidden rounded-2xl border border-[#2b3344] bg-[#151b28] shadow-[0_28px_90px_rgba(0,0,0,0.42)] md:min-h-[590px] md:grid-cols-[0.88fr_1.12fr]">
        <aside className="relative hidden flex-col justify-between overflow-hidden border-r border-[#2b3344] bg-[#111923] p-10 md:flex lg:p-12">
          <div className="absolute inset-0 opacity-40" style={{ backgroundImage: 'linear-gradient(135deg, transparent 48%, rgba(91, 75, 255, 0.18) 48.2%, transparent 48.6%), linear-gradient(45deg, transparent 67%, rgba(15, 157, 138, 0.14) 67.2%, transparent 67.6%)' }} />
          <div className="relative">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#5b4bff] text-xl font-black shadow-lg shadow-[#5b4bff]/20">V</div>
              <span className="text-sm font-bold tracking-wide">VirtuFit AI</span>
            </div>
            <div className="mt-20">
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#8993aa]">Workspace / 01</p>
              <h1 className="mt-5 text-4xl font-bold leading-tight">Quản trị<br />hệ thống</h1>
              <div className="mt-6 h-1 w-14 rounded-full bg-[#0f9d8a]" />
              <p className="mt-5 max-w-[230px] text-sm leading-6 text-[#a2acc0]">Cổng truy cập dành cho đội ngũ vận hành VirtuFit AI.</p>
            </div>
          </div>
          <div className="relative flex items-center justify-between border-t border-[#2b3344] pt-5 text-[10px] font-semibold uppercase tracking-[0.14em] text-[#778196]">
            <span>VirtuFit / Admin</span>
            <span className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-[#0fbd8e]" /> Secure access</span>
          </div>
        </aside>

        <section className="flex items-center justify-center px-6 py-9 sm:px-10 md:px-12 lg:px-16">
          <div className="w-full max-w-md">
            <div className="mb-9 flex items-center gap-3 md:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#5b4bff] text-lg font-black">V</div>
              <span className="font-bold">VirtuFit AI</span>
            </div>

            <div className="mb-8">
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#0fbd8e]">Cổng quản trị</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight">Đăng nhập</h2>
              <p className="mt-2 text-sm text-[#9aa5ba]">Nhập thông tin tài khoản để tiếp tục.</p>
            </div>

            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <div>
                <label htmlFor="login-account" className="mb-2 block text-xs font-semibold text-[#d6dbea]">Tài khoản</label>
                <input
                  id="login-account"
                  type="text"
                  autoComplete="username"
                  value={account}
                  onChange={(event) => { setAccount(event.target.value); setError(''); }}
                  placeholder="Nhập tài khoản"
                  className="w-full rounded-lg border border-[#394356] bg-[#101621] px-4 py-3.5 text-sm text-white outline-none transition-colors placeholder:text-[#657087] hover:border-[#56617a] focus:border-[#7568ff] focus:ring-2 focus:ring-[#5b4bff]/20"
                  required
                />
              </div>

              <div>
                <label htmlFor="login-password" className="mb-2 block text-xs font-semibold text-[#d6dbea]">Mật khẩu</label>
                <div className="relative">
                  <input
                    id="login-password"
                    type={isPasswordVisible ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => { setPassword(event.target.value); setError(''); }}
                    placeholder="Nhập mật khẩu"
                    className="w-full rounded-lg border border-[#394356] bg-[#101621] px-4 py-3.5 pr-16 text-sm text-white outline-none transition-colors placeholder:text-[#657087] hover:border-[#56617a] focus:border-[#7568ff] focus:ring-2 focus:ring-[#5b4bff]/20"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setPasswordVisible((visible) => !visible)}
                    aria-label={isPasswordVisible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                    aria-pressed={isPasswordVisible}
                    className="absolute inset-y-0 right-3 text-xs font-semibold text-[#9aa5ba] hover:text-white"
                  >
                    {isPasswordVisible ? 'Ẩn' : 'Hiện'}
                  </button>
                </div>
              </div>

              {error && (
                <div role="alert" className="rounded-lg border border-[#e5484d]/40 bg-[#e5484d]/10 px-3 py-2.5 text-sm text-[#ff8588]">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="mt-1 flex w-full items-center justify-center gap-2 rounded-lg bg-[#5b4bff] px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-[#5b4bff]/20 transition-colors hover:bg-[#6b5eff] focus:outline-none focus:ring-2 focus:ring-[#8e85ff] focus:ring-offset-2 focus:ring-offset-[#151b28] disabled:cursor-wait disabled:opacity-60"
              >
                {isSubmitting ? 'Đang đăng nhập…' : 'Đăng nhập hệ thống'}
                <span aria-hidden="true">→</span>
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
};

export default Login;
