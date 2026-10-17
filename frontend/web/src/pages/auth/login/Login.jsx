import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (email === 'admin@virtufit.vn' && password.length >= 6) {
      localStorage.setItem('userRole', 'admin');
      navigate('/admin');
    } else if (email === 'kho@virtufit.vn' && password.length >= 6) {
      localStorage.setItem('userRole', 'warehouse');
      navigate('/warehouse');
    } else {
      setError('Tài khoản không tồn tại hoặc sai mật khẩu!');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-900 font-sans">
      <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-slate-700 mx-4">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-indigo-600 rounded-2xl flex items-center justify-center font-bold text-white text-3xl mx-auto mb-4 shadow-lg">
            V
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">VirtuFit AI</h1>
          <p className="text-slate-400">Đăng nhập hệ thống quản trị Web</p>
        </div>
        
        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">Email đăng nhập</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@virtufit.vn"
              className="w-full p-3.5 rounded-xl bg-slate-900/50 border border-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none text-white transition-all"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">Mật khẩu</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full p-3.5 rounded-xl bg-slate-900/50 border border-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none text-white transition-all"
              required
            />
          </div>
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg text-sm font-medium text-center">
              {error}
            </div>
          )}
          <button 
            type="submit" 
            className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 px-4 rounded-xl transition-colors shadow-lg shadow-indigo-600/30"
          >
            Đăng nhập hệ thống
          </button>
        </form>
        
        <div className="mt-8 pt-6 border-t border-slate-700 text-center">
          <p className="text-xs text-slate-500">
            Tài khoản Admin: admin@virtufit.vn | mk: 123456
            <br />
            Tài khoản Kho: kho@virtufit.vn | mk: 123456
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;