import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

// Import 2 module đã tách
import CustomerAccounts from '../customer-accounts/CustomerAccounts';
import StaffAccounts from '../staff-accounts/StaffAccounts';
import Overview from './Overview';
import RevenueReports from '../revenue-reports/RevenueReports';
import InteractionReports from '../interaction-reports/InteractionReports';
import Notifications from './Notifications';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';
  
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(3);
  
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
        <NavItem id="notif" icon="🔔" label="Thông báo" badge={unreadNotificationCount || undefined} />
        
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
          <button type="button" onClick={() => setSearchParams({ tab: 'notif' })} aria-label="Mở thông báo" title="Thông báo" className="text-[#9aa2c0] hover:text-white transition-colors text-lg">🔔</button>
          <div className="w-9 h-9 rounded-full bg-[#5b4bff] flex items-center justify-center font-bold text-sm shadow-md cursor-pointer text-white">AD</div>
        </header>

        <div className="p-4 md:p-6 max-w-7xl mx-auto w-full">
          
          {activeTab === 'overview' && <Overview />}

          {activeTab === 'report' && <RevenueReports />}

          {activeTab === 'stats' && <InteractionReports />}

          {/* TAB: KHÁCH HÀNG (Gọi Module) */}
          {activeTab === 'customers' && <CustomerAccounts />}

          {/* TAB: NHÂN VIÊN (Gọi Module) */}
          {activeTab === 'staff' && <StaffAccounts />}

          {/* TAB: THÔNG BÁO */}
          <Notifications isHidden={activeTab !== 'notif'} onUnreadCountChange={setUnreadNotificationCount} />
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