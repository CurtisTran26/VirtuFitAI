import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Import các Module tĩnh đã tách
import Products from '../products/Products';
import Catalog from '../categories/Catalog';
import StockAdjustments from '../stock-adjustments/StockAdjustments';
import QRCodes from '../qr-codes/QRCodes';

// ==========================================
// MOCK DATA CHO CÁC TAB CHƯA TÁCH MODULE
// ==========================================
const mockReturns = [
  { id: 'RT-0231', order: '#VF-1210', product: 'Áo sơ mi linen (Trắng/L)', reason: 'Không vừa size', status: 'Chờ tiếp nhận', badge: 'bg-[#3a2e12] text-[#e8930c]' },
  { id: 'RT-0229', order: '#VF-1198', product: 'Quần jeans slim (Xanh navy/L)', reason: 'Đổi ý', status: 'Đã nhập kho', badge: 'bg-[#0f2e24] text-[#12a66a]' },
  { id: 'RT-0227', order: '#VF-1185', product: 'Váy xếp ly (Be/S)', reason: 'Giao nhầm màu', status: 'Không đạt', badge: 'bg-[#3a1a1e] text-[#e5484d]' },
];

const mockCustom = [
  { id: 'CD-0045', customer: 'Nguyễn Minh Anh', detail: 'Áo blazer oversize, vải tweed xám', designer: 'Designer: Ngô Thanh Vy', date: '12/10/2026', step: 1 },
  { id: 'CD-0044', customer: 'Trần Bảo Ngọc', detail: 'Đầm dạ hội lụa đỏ đô, tay bồng', designer: 'Designer: Ngô Thanh Vy', date: '18/10/2026', step: 2 },
  { id: 'CD-0042', customer: 'Lê Hoàng Nam', detail: 'Sơ mi lanh may đo, cổ Mandarin', designer: 'Designer: Ngô Thanh Vy', date: '06/10/2026', step: 4 },
];

const WarehouseDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('orders'); // Tab mặc định khi vào
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  
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
          <button className="text-[#92a9ad] hover:text-white transition-colors text-lg">🔔</button>
          <div className="w-9 h-9 rounded-full bg-[#0f9d8a] flex items-center justify-center font-bold text-sm shadow-md cursor-pointer text-white">NK</div>
        </header>

        <div className="p-4 md:p-6 max-w-7xl mx-auto w-full">
          
          {/* GỌI CÁC COMPONENT ĐÃ TÁCH MODULE */}
          {activeTab === 'products' && <Products />}
          {activeTab === 'catalog' && <Catalog />}
          {activeTab === 'qr' && <QRCodes />}
          {activeTab === 'stock' && <StockAdjustments />}

          {/* TAB: HÀNG TRẢ */}
          {activeTab === 'returns' && (
            <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
              <table className="w-full text-left min-w-[620px]">
                <thead>
                  <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
                    <th className="p-4 font-semibold">Mã trả</th><th className="p-4 font-semibold">Đơn gốc</th>
                    <th className="p-4 font-semibold">Sản phẩm</th><th className="p-4 font-semibold">Lý do</th>
                    <th className="p-4 font-semibold">Trạng thái</th><th className="p-4"></th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {mockReturns.map((r, i) => (
                    <tr key={i} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                      <td className="p-4 font-bold">{r.id}</td><td className="p-4">{r.order}</td><td className="p-4">{r.product}</td><td className="p-4">{r.reason}</td>
                      <td className="p-4"><span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${r.badge}`}>{r.status}</span></td>
                      <td className="p-4">
                        {r.status === 'Chờ tiếp nhận' && <button className="bg-[#0f9d8a] text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#0b7a6c]">Kiểm tra</button>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB: ĐƠN CẦN CHUẨN BỊ */}
          {activeTab === 'orders' && (
            <div className="space-y-4">
              <div className="flex gap-2 flex-wrap mb-4">
                <button className="bg-[#12383a] text-[#0f9d8a] border border-[#0f9d8a] px-4 py-2 rounded-xl text-sm font-semibold">Tất cả</button>
                <button className="bg-[#152427] text-[#92a9ad] border border-[#24383b] px-4 py-2 rounded-xl text-sm font-semibold">Chờ chuẩn bị</button>
                <button className="bg-[#152427] text-[#92a9ad] border border-[#24383b] px-4 py-2 rounded-xl text-sm font-semibold">Đang đóng gói</button>
              </div>
              <div className="bg-[#152427] border border-[#24383b] rounded-2xl overflow-x-auto">
                <table className="w-full text-left min-w-[620px]">
                  <thead>
                    <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
                      <th className="p-4 font-semibold">Mã đơn</th><th className="p-4 font-semibold">Khách hàng</th>
                      <th className="p-4 font-semibold">Số SP</th><th className="p-4 font-semibold">Thanh toán</th>
                      <th className="p-4 font-semibold">Trạng thái</th><th className="p-4"></th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    <tr className="border-b border-[#24383b] hover:bg-[#12383a]/30 transition-colors">
                      <td className="p-4 font-bold">#VF-1284</td><td className="p-4">Nguyễn Minh Anh</td><td className="p-4">3</td><td className="p-4">VNPay – Đã TT</td>
                      <td className="p-4"><span className="bg-[#3a2e12] text-[#e8930c] px-3 py-1 rounded-full text-xs font-bold">Chờ chuẩn bị</span></td>
                      <td className="p-4"><button className="bg-[#0f9d8a] text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#0b7a6c]">Chi tiết</button></td>
                    </tr>
                    <tr className="hover:bg-[#12383a]/30 transition-colors">
                      <td className="p-4 font-bold">#VF-1281</td><td className="p-4">Phạm Thu Hà</td><td className="p-4">2</td><td className="p-4">VNPay – Đã TT</td>
                      <td className="p-4"><span className="bg-[#17284a] text-[#3b82f6] px-3 py-1 rounded-full text-xs font-bold">Đang đóng gói</span></td>
                      <td className="p-4"><button className="bg-[#0f9d8a] text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-[#0b7a6c]">Chi tiết</button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB: ĐƠN THIẾT KẾ RIÊNG */}
          {activeTab === 'custom' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockCustom.map((c, i) => (
                <div key={i} className="bg-[#152427] border border-[#24383b] p-5 rounded-2xl flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-lg">{c.id}</span>
                    <span className="bg-[#12383a] text-[#0f9d8a] px-3 py-1 rounded-full text-xs font-bold">{['Tiếp nhận', 'Chuẩn bị vật liệu', 'Đang may', 'QC', 'Đang giao'][c.step]}</span>
                  </div>
                  <div>
                    <div className="font-bold">{c.customer}</div>
                    <div className="text-[#92a9ad] text-sm mt-1 leading-relaxed">{c.detail}<br/>{c.designer}</div>
                  </div>
                  <div className="flex items-center gap-2 mt-2 pt-4 border-t border-[#24383b]">
                    <select className="bg-[#0e1a1c] border border-[#24383b] text-white px-3 py-2 rounded-lg text-xs flex-1">
                      {['Đã tiếp nhận', 'Chuẩn bị vật liệu', 'Đang may', 'Hoàn thiện & QC', 'Đang giao'].map((s, idx) => (
                        <option key={idx} selected={idx === c.step}>{s}</option>
                      ))}
                    </select>
                    <button className="bg-[#0f9d8a] text-white px-4 py-2 rounded-lg text-xs font-bold hover:bg-[#0b7a6c]">Cập nhật</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* CÁC TAB ĐANG PHÁT TRIỂN (Lịch sử, Thông báo) */}
          {['hist', 'notif'].includes(activeTab) && (
            <div className="bg-[#152427] border border-[#24383b] p-12 rounded-2xl flex flex-col items-center justify-center text-[#92a9ad] min-h-[300px]">
              <div className="text-4xl mb-4">🚧</div><h3 className="text-lg font-bold text-white mb-2">Đang phát triển...</h3>
            </div>
          )}
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