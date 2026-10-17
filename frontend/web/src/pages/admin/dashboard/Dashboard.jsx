import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

// Import 2 module đã tách
import CustomerAccounts from '../customer-accounts/CustomerAccounts';
import StaffAccounts from '../staff-accounts/StaffAccounts';

// Dữ liệu mẫu (Mock Data) cho các tab
const mockTopProducts = [
  { name: 'Áo sơ mi linen', sales: 92 },
  { name: 'Đầm midi hoa', sales: 78 },
  { name: 'Quần jeans slim', sales: 64 },
  { name: 'Áo khoác bomber', sales: 51 },
  { name: 'Váy xếp ly', sales: 43 }
];

const mockReports = Array.from({ length: 6 }).map((_, i) => ({
  date: `${String(30 - i).padStart(2, '0')}/09/2026`,
  orders: 45 + i * 2,
  online: '14.250.000₫',
  offline: '4.500.000₫',
  refund: i % 2,
  revenue: '18.750.000₫'
}));

const mockStats = [
  { name: 'Áo sơ mi linen', qr: '1.420', view: '3.260', try: '890', cvr: '62%' },
  { name: 'Đầm midi hoa', qr: '1.180', view: '2.940', try: '1.010', cvr: '85%' },
  { name: 'Quần jeans slim', qr: '960', view: '2.410', try: '640', cvr: '66%' },
];

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';
  
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  
  // State quản lý Modal Đăng xuất
  const [isLogoutModalOpen, setLogoutModalOpen] = useState(false);

  const handleLogoutClick = () => {
    setLogoutModalOpen(true);
  };

  const handleConfirmLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('accessToken'); 
    navigate('/login');
  };

  const NavItem = ({ id, icon, label, badge }) => (
    <button
      onClick={() => { 
        setSearchParams({ tab: id }); 
        setSidebarOpen(false); 
      }}
      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm transition-colors ${
        activeTab === id 
          ? 'bg-[#26235a] text-[#5b4bff]' 
          : 'text-[#9aa2c0] hover:bg-[#0f1220] hover:text-[#eef0f8]'
      }`}
    >
      <span>{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {badge && <span className="bg-[#e5484d] text-white text-[10px] px-2 py-0.5 rounded-full">{badge}</span>}
    </button>
  );

  return (
    <div className="min-h-screen bg-[#0f1220] text-[#eef0f8] font-sans flex">
      {/* Overlay Sidebar cho Mobile */}
      {isSidebarOpen && <div className="fixed inset-0 bg-black/50 z-20 md:hidden" onClick={() => setSidebarOpen(false)}></div>}

      {/* Sidebar Navigation */}
      <aside className={`fixed md:sticky top-0 z-30 h-screen w-[240px] bg-[#181c30] border-r border-[#262b45] p-4 flex flex-col gap-1 transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="flex items-center gap-3 font-extrabold text-lg px-2 pb-4 pt-1">
          <div className="w-[34px] h-[34px] rounded-lg bg-gradient-to-br from-[#5b4bff] to-[#b46bff] flex items-center justify-center text-white text-base shadow-lg">V</div>
          VirtuFit AI
        </div>
        
        <div className="text-[11px] font-bold text-[#9aa2c0] uppercase tracking-wider px-2 pt-4 pb-1">Thống kê</div>
        <NavItem id="overview" icon="📊" label="Tổng quan doanh thu" />
        <NavItem id="report" icon="🧾" label="Báo cáo doanh thu" />
        <NavItem id="stats" icon="📱" label="QR · Lượt xem · Thử đồ" />
        
        <div className="text-[11px] font-bold text-[#9aa2c0] uppercase tracking-wider px-2 pt-4 pb-1">Tài khoản</div>
        <NavItem id="customers" icon="👥" label="Khách hàng" />
        <NavItem id="staff" icon="🛡️" label="Nhân viên & phân quyền" />
        
        <div className="text-[11px] font-bold text-[#9aa2c0] uppercase tracking-wider px-2 pt-4 pb-1">Hệ thống</div>
        <NavItem id="notif" icon="🔔" label="Thông báo" badge="3" />
        
        <div className="flex-1"></div>
        {/* Nút bấm GỌI MODAL ĐĂNG XUẤT */}
        <button onClick={handleLogoutClick} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-[#9aa2c0] hover:bg-[#0f1220] hover:text-[#eef0f8] transition-colors">
          <span>↩</span> Đăng xuất
        </button>
      </aside>

      <main className="flex-1 min-w-0 flex flex-col h-screen overflow-y-auto">
        <header className="sticky top-0 z-10 flex items-center gap-3 px-6 py-4 bg-[#181c30] border-b border-[#262b45]">
          <button className="md:hidden text-[#9aa2c0] px-2 text-xl" onClick={() => setSidebarOpen(true)}>☰</button>
          <h2 className="text-lg font-bold">
            {activeTab === 'overview' && 'Tổng quan doanh thu'}
            {activeTab === 'report' && 'Báo cáo doanh thu'}
            {activeTab === 'stats' && 'Thống kê quét QR, lượt xem & thử đồ'}
            {activeTab === 'customers' && 'Tài khoản khách hàng'}
            {activeTab === 'staff' && 'Nhân viên & phân quyền'}
            {activeTab === 'notif' && 'Thông báo'}
          </h2>
          <div className="flex-1"></div>
          <button className="text-[#9aa2c0] hover:text-white transition-colors text-lg">🔔</button>
          <div className="w-9 h-9 rounded-full bg-[#5b4bff] flex items-center justify-center font-bold text-sm shadow-md cursor-pointer text-white">AD</div>
        </header>

        <div className="p-4 md:p-6 max-w-7xl mx-auto w-full">
          
          {/* TAB: TỔNG QUAN DOANH THU */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  {l: 'Doanh thu tháng', v: '482,5 tr₫', c: '▲ 12,4%', p: true}, 
                  {l: 'Đơn hàng', v: '1.284', c: '▲ 8,1%', p: true}, 
                  {l: 'Giá trị TB/đơn', v: '375 nghìn₫', c: '▼ 2,3%', p: false}, 
                  {l: 'Tỷ lệ thử đồ → mua', v: '18,7%', c: '▲ 3,2%', p: true}
                ].map((k, i) => (
                  <div key={i} className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl">
                    <div className="text-xs font-semibold text-[#9aa2c0] mb-2">{k.l}</div>
                    <div className="text-2xl font-bold mb-1">{k.v}</div>
                    <div className={`text-xs font-bold ${k.p ? 'text-[#12a66a]' : 'text-[#e5484d]'}`}>{k.c}</div>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 bg-[#181c30] border border-[#262b45] p-5 rounded-2xl flex flex-col">
                  <h3 className="font-bold text-base mb-4">Doanh thu 12 tháng (triệu ₫)</h3>
                  <div className="flex-1 min-h-[220px] border border-dashed border-[#262b45] rounded-xl flex items-center justify-center text-[#9aa2c0]">
                    [Khu vực gắn Biểu đồ Chart.js]
                  </div>
                </div>
                <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl">
                  <h3 className="font-bold text-base mb-4">Top sản phẩm</h3>
                  <div className="space-y-4">
                    {mockTopProducts.map((p, i) => (
                      <div key={i}>
                        <div className="flex justify-between text-sm mb-1.5">
                          <span>{p.name}</span><span className="font-bold text-[#9aa2c0]">{p.sales} đơn</span>
                        </div>
                        <div className="h-2 w-full bg-[#262b45] rounded-full overflow-hidden">
                          <div className="h-full bg-[#5b4bff] rounded-full" style={{width: `${p.sales}%`}}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB: BÁO CÁO DOANH THU */}
          {activeTab === 'report' && (
            <div className="space-y-4">
              <div className="bg-[#181c30] border border-[#262b45] p-4 rounded-2xl flex flex-wrap gap-4 items-end">
                <div className="flex-1 min-w-[140px]"><label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Từ ngày</label><input type="date" defaultValue="2026-09-01" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" /></div>
                <div className="flex-1 min-w-[140px]"><label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Đến ngày</label><input type="date" defaultValue="2026-09-30" className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]" /></div>
                <div className="flex-1 min-w-[140px]"><label className="block text-xs font-semibold text-[#9aa2c0] mb-2">Kênh bán</label><select className="w-full bg-[#0f1220] border border-[#262b45] rounded-xl px-3 py-2.5 text-sm outline-none focus:border-[#5b4bff]"><option>Tất cả</option><option>Online (VNPay/COD)</option><option>Tại quầy (POS)</option></select></div>
                <button className="bg-[#5b4bff] text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-[#4a3ecc]">Áp dụng</button>
              </div>
              <div className="bg-[#181c30] border border-[#262b45] rounded-2xl overflow-x-auto">
                <table className="w-full text-left min-w-[560px]">
                  <thead>
                    <tr className="border-b border-[#262b45] text-[#9aa2c0] text-xs">
                      <th className="p-4 font-semibold">Ngày</th><th className="p-4 font-semibold">Số đơn</th>
                      <th className="p-4 font-semibold">Online</th><th className="p-4 font-semibold">Tại quầy</th>
                      <th className="p-4 font-semibold">Hoàn/hủy</th><th className="p-4 font-semibold">Doanh thu</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {mockReports.map((r, i) => (
                      <tr key={i} className="border-b border-[#262b45] last:border-0 hover:bg-[#181c30]/80 transition-colors">
                        <td className="p-4">{r.date}</td><td className="p-4">{r.orders}</td>
                        <td className="p-4">{r.online}</td><td className="p-4">{r.offline}</td>
                        <td className="p-4">{r.refund}</td><td className="p-4 font-bold">{r.revenue}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB: THỐNG KÊ QR & THỬ ĐỒ */}
          {activeTab === 'stats' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl"><div className="text-xs font-semibold text-[#9aa2c0] mb-2">Lượt quét QR</div><div className="text-2xl font-bold mb-1">8.420</div><div className="text-xs font-bold text-[#12a66a]">▲ 14%</div></div>
                <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl"><div className="text-xs font-semibold text-[#9aa2c0] mb-2">Lượt xem sản phẩm</div><div className="text-2xl font-bold mb-1">21.960</div><div className="text-xs font-bold text-[#12a66a]">▲ 9%</div></div>
                <div className="bg-[#181c30] border border-[#262b45] p-5 rounded-2xl"><div className="text-xs font-semibold text-[#9aa2c0] mb-2">Lượt thử đồ AI</div><div className="text-2xl font-bold mb-1">5.318</div><div className="text-xs font-bold text-[#12a66a]">▲ 22%</div></div>
              </div>
              <div className="bg-[#181c30] border border-[#262b45] rounded-2xl overflow-x-auto">
                <table className="w-full text-left min-w-[560px]">
                  <thead>
                    <tr className="border-b border-[#262b45] text-[#9aa2c0] text-xs">
                      <th className="p-4 font-semibold">Sản phẩm</th><th className="p-4 font-semibold">Quét QR</th>
                      <th className="p-4 font-semibold">Lượt xem</th><th className="p-4 font-semibold">Thử đồ</th>
                      <th className="p-4 font-semibold">Chuyển đổi</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {mockStats.map((s, i) => (
                      <tr key={i} className="border-b border-[#262b45] last:border-0 hover:bg-[#181c30]/80 transition-colors">
                        <td className="p-4">{s.name}</td><td className="p-4">{s.qr}</td>
                        <td className="p-4">{s.view}</td><td className="p-4">{s.try}</td>
                        <td className="p-4"><span className="bg-[#0f2e24] text-[#12a66a] px-3 py-1 rounded-full text-xs font-bold">{s.cvr}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB: KHÁCH HÀNG (Gọi Module) */}
          {activeTab === 'customers' && <CustomerAccounts />}

          {/* TAB: NHÂN VIÊN (Gọi Module) */}
          {activeTab === 'staff' && <StaffAccounts />}

          {/* TAB: THÔNG BÁO */}
          {activeTab === 'notif' && (
            <div className="bg-[#181c30] border border-[#262b45] p-12 rounded-2xl flex flex-col items-center justify-center text-[#9aa2c0] min-h-[300px]">
              <div className="text-4xl mb-4">🚧</div>
              <h3 className="text-lg font-bold text-white mb-2">Đang phát triển...</h3>
            </div>
          )}
        </div>
      </main>

      {/* ==========================================
          MODAL XÁC NHẬN ĐĂNG XUẤT
      ========================================== */}
      {isLogoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#181c30] border border-[#262b45] rounded-2xl w-full max-w-sm p-6 shadow-2xl animate-fade-in-up">
            <h3 className="text-lg font-bold mb-2">Xác nhận đăng xuất</h3>
            <p className="text-[#9aa2c0] text-sm mb-6">Bạn có chắc chắn muốn đăng xuất khỏi trang quản trị?</p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setLogoutModalOpen(false)} 
                className="px-5 py-2.5 rounded-xl text-sm font-bold border border-[#262b45] text-[#9aa2c0] hover:text-white hover:bg-[#262b45] transition-colors"
              >
                Hủy
              </button>
              <button 
                onClick={handleConfirmLogout} 
                className="bg-[#e5484d] text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-[#c93b40] transition-colors"
              >
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;