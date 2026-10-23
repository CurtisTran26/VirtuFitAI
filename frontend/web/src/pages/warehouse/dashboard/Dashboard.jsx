import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Import các Module tĩnh đã tách
import Products from '../products/Products';
import Catalog from '../categories/Catalog';
import StockAdjustments from '../stock-adjustments/StockAdjustments';
import QRCodes from '../qr-codes/QRCodes';
import Returns from '../returns/Returns';
import Orders from '../orders/Orders';
import CustomOrders from '../custom-orders/CustomOrders';
import Notifications from './Notifications';

// ==========================================
// MOCK DATA CHO CÁC TAB CHƯA TÁCH MODULE
// ==========================================
const mockStockHistory = [
  { id: 1, date: '30/09 09:12', product: 'Áo sơ mi linen (Trắng/L)', type: 'Xuất', quantity: -2, reason: 'Hàng lỗi / hư hỏng', user: 'kho@virtufit.vn' },
  { id: 2, date: '29/09 16:40', product: 'Đầm midi hoa (Đỏ đô/M)', type: 'Nhập', quantity: 20, reason: 'Nhập hàng mới', user: 'kho@virtufit.vn' },
  { id: 3, date: '29/09 10:05', product: 'Quần jeans slim (Xanh navy/L)', type: 'Nhập', quantity: 5, reason: 'Hàng trả nhập lại kho', user: 'kho@virtufit.vn' },
];

const WarehouseDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('orders'); // Tab mặc định khi vào
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(3);
  
  // Trạng thái Quản lý Modal Đăng Xuất
  const [isLogoutModalOpen, setLogoutModalOpen] = useState(false);

  // Xử lý Hủy/Mở Modal Đăng xuất
  const handleLogoutClick = () => {
    setLogoutModalOpen(true);
  };

  // Xử lý Đồng ý Đăng xuất
  const handleConfirmLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('accessToken');
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
        <NavItem id="catalog" icon="🏷️" label="Danh mục · Màu · Size" />
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
            {activeTab === 'catalog' && 'Danh mục, màu, size & bảng size'}
            {activeTab === 'qr' && 'Tạo & tải mã QR sản phẩm'}
            {activeTab === 'stock' && 'Danh sách tồn kho'}
            {activeTab === 'hist' && 'Lịch sử điều chỉnh tồn kho'}
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

          {activeTab === 'returns' && <Returns />}

          {activeTab === 'orders' && <Orders />}

          {activeTab === 'custom' && <CustomOrders />}

          {/* TAB: LỊCH SỬ ĐIỀU CHỈNH TỒN KHO */}
          {activeTab === 'hist' && (
            <div className="space-y-4">
              <h1 className="text-lg font-bold">Lịch sử điều chỉnh tồn kho</h1>
              <div className="bg-[#152427] border border-[#24383b] rounded-xl overflow-x-auto">
                <table className="w-full min-w-[760px] text-left">
                  <thead>
                    <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
                      <th className="px-4 py-3 font-semibold">Thời gian</th>
                      <th className="px-4 py-3 font-semibold">Sản phẩm</th>
                      <th className="px-4 py-3 font-semibold">Loại</th>
                      <th className="px-4 py-3 font-semibold">Số lượng</th>
                      <th className="px-4 py-3 font-semibold">Lý do</th>
                      <th className="px-4 py-3 font-semibold">Người thực hiện</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {mockStockHistory.map((entry) => (
                      <tr key={entry.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                        <td className="px-4 py-3 text-[#c5d2d2] whitespace-nowrap">{entry.date}</td>
                        <td className="px-4 py-3">{entry.product}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${entry.type === 'Nhập' ? 'bg-[#0f2e24] text-[#12a66a]' : 'bg-[#3a2e12] text-[#e8930c]'}`}>
                            {entry.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-bold tabular-nums">{entry.quantity > 0 ? `+${entry.quantity}` : entry.quantity}</td>
                        <td className="px-4 py-3">{entry.reason}</td>
                        <td className="px-4 py-3 text-[#c5d2d2]">{entry.user}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

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