import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Import các Module tĩnh đã tách
import Products from '../products/Products';
import Catalog from '../categories/Catalog';
import StockAdjustments from '../stock-adjustments/StockAdjustments';
import StockHistory from '../stock-adjustments/StockHistory';
import QRCodes from '../qr-codes/QRCodes';
import Returns from '../returns/Returns';
import Orders from '../orders/Orders';
import CustomOrders from '../custom-orders/CustomOrders';
import Notifications from './Notifications';
import apiClient from '../../../utils/apiClient';

// ==========================================
// MOCK DATA CHO CÁC TAB CHƯA TÁCH MODULE
// ==========================================
const WarehouseDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('products'); // Mở danh sách sản phẩm sau khi đăng nhập
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  
  // Trạng thái Quản lý Modal Đăng Xuất
  const [isLogoutModalOpen, setLogoutModalOpen] = useState(false);

  // Xử lý Hủy/Mở Modal Đăng xuất
  const handleLogoutClick = () => {
    setLogoutModalOpen(true);
  };

  // Xử lý Đồng ý Đăng xuất
  const handleConfirmLogout = () => {
    apiClient.post('auth/logout', {}).catch(() => {});
    localStorage.removeItem('userRole');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userName');
    navigate('/login');
  };

  // Component Nút Sidebar
  const NavItem = ({ id, icon, label, badge }) => (
    <button
      onClick={() => { setActiveTab(id); setSidebarOpen(false); }}
      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm transition-colors ${
        activeTab === id 
          ? 'bg-[#12383a] text-[#0f9d8a]' 
          : 'text-[#92a9ad] hover:bg-[#0e1a1c] hover:text-[#e8f2f1]'
      }`}
    >
      <span>{icon}</span>
      <span className="flex-1 text-left">{label}</span>
      {badge && <span className="bg-[#e5484d] text-white text-[10px] px-2 py-0.5 rounded-full">{badge}</span>}
    </button>
  );

  return (
    <div className="min-h-screen bg-[#0e1a1c] text-[#e8f2f1] font-sans flex">
      {/* Lớp phủ màn mờ (Chỉ hiện trên Mobile khi mở menu) */}
      {isSidebarOpen && <div className="fixed inset-0 bg-black/50 z-20 md:hidden" onClick={() => setSidebarOpen(false)}></div>}

      {/* ==========================================
          CỘT SIDEBAR MENU TRÁI
      ========================================== */}
      <aside className={`fixed md:sticky top-0 z-30 h-screen w-[250px] bg-[#152427] border-r border-[#24383b] p-4 flex flex-col gap-1 transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="flex items-center gap-3 font-extrabold text-lg px-2 pb-4 pt-1">
          <div className="w-[34px] h-[34px] rounded-lg bg-gradient-to-br from-[#0f9d8a] to-[#38c9a8] flex items-center justify-center text-white text-base shadow-lg">V</div>
          VirtuFit AI
        </div>
        
        <div className="text-[11px] font-bold text-[#92a9ad] uppercase tracking-wider px-2 pt-4 pb-1">Sản phẩm</div>
        <NavItem id="products" icon="👕" label="Danh sách sản phẩm" />
        <NavItem id="catalog" icon="🏷️" label="Danh mục & bảng size" />
        <NavItem id="qr" icon="🔳" label="Mã QR sản phẩm" />
        
        <div className="text-[11px] font-bold text-[#92a9ad] uppercase tracking-wider px-2 pt-4 pb-1">Kho</div>
        <NavItem id="stock" icon="📦" label="Tồn kho" />
        <NavItem id="hist" icon="🕘" label="Lịch sử điều chỉnh" />
        <NavItem id="returns" icon="↩️" label="Hàng trả" />

        <div className="text-[11px] font-bold text-[#92a9ad] uppercase tracking-wider px-2 pt-4 pb-1">Đơn hàng</div>
        <NavItem id="orders" icon="🚚" label="Đơn cần chuẩn bị" />
        <NavItem id="custom" icon="✂️" label="Đơn thiết kế riêng" />

        <div className="text-[11px] font-bold text-[#92a9ad] uppercase tracking-wider px-2 pt-4 pb-1">Hệ thống</div>
        <NavItem id="notif" icon="🔔" label="Thông báo" badge={unreadNotificationCount || undefined} />
        
        <div className="flex-1"></div>
        {/* Nút bấm GỌI MODAL ĐĂNG XUẤT */}
        <button onClick={handleLogoutClick} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm text-[#92a9ad] hover:bg-[#0e1a1c] hover:text-[#e8f2f1] transition-colors">
          <span>⏻</span> Đăng xuất
        </button>
      </aside>

      {/* ==========================================
          KHU VỰC HIỂN THỊ NỘI DUNG CHÍNH (MAIN)
      ========================================== */}
      <main className="flex-1 min-w-0 flex flex-col h-screen overflow-y-auto">
        <header className="sticky top-0 z-10 flex items-center gap-3 px-6 py-4 bg-[#152427] border-b border-[#24383b]">
          <button className="md:hidden text-[#92a9ad] px-2 text-xl" onClick={() => setSidebarOpen(true)}>☰</button>
          <h2 className="text-lg font-bold">
            {activeTab === 'products' && 'Danh sách sản phẩm'}
            {activeTab === 'catalog' && 'Danh mục & bảng size'}
            {activeTab === 'qr' && 'Tạo & tải mã QR sản phẩm'}
            {activeTab === 'stock' && 'Tồn kho'}
            {activeTab === 'hist' && 'Lịch sử điều chỉnh tồn'}
            {activeTab === 'returns' && 'Tiếp nhận & kiểm tra hàng trả'}
            {activeTab === 'orders' && 'Đơn cần chuẩn bị'}
            {activeTab === 'custom' && 'Đơn thiết kế riêng'}
            {activeTab === 'notif' && 'Thông báo'}
          </h2>
          <div className="flex-1"></div>
          <button
            type="button"
            onClick={() => setActiveTab('notif')}
            aria-label="Mở thông báo"
            title="Thông báo"
            className="text-[#92a9ad] hover:text-white transition-colors text-lg"
          >
            🔔
          </button>
          <div className="w-9 h-9 rounded-full bg-[#0f9d8a] flex items-center justify-center font-bold text-sm shadow-md cursor-pointer text-white">NK</div>
        </header>

        <div className="p-4 md:p-6 max-w-7xl mx-auto w-full">
          
          {/* GỌI CÁC COMPONENT ĐÃ TÁCH MODULE */}
          {activeTab === 'products' && <Products />}
          {activeTab === 'catalog' && <Catalog />}
          {activeTab === 'qr' && <QRCodes />}
          {activeTab === 'stock' && <StockAdjustments />}
          {activeTab === 'hist' && <StockHistory />}

          {activeTab === 'returns' && <Returns />}

          {activeTab === 'orders' && <Orders />}

          {activeTab === 'custom' && <CustomOrders />}

          <Notifications isHidden={activeTab !== 'notif'} onUnreadCountChange={setUnreadNotificationCount} />
        </div>
      </main>

      {/* ==========================================
          MODAL XÁC NHẬN ĐĂNG XUẤT (Nằm đè lên trên cùng)
      ========================================== */}
      {isLogoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#152427] border border-[#24383b] rounded-2xl w-full max-w-sm p-6 shadow-2xl animate-fade-in-up">
            <h3 className="text-lg font-bold mb-2">Xác nhận đăng xuất</h3>
            <p className="text-[#92a9ad] text-sm mb-6">Bạn có chắc chắn muốn đăng xuất khỏi hệ thống kho?</p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setLogoutModalOpen(false)} 
                className="px-5 py-2.5 rounded-xl text-sm font-bold border border-[#24383b] text-[#92a9ad] hover:text-white hover:bg-[#24383b] transition-colors"
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

export default WarehouseDashboard;
