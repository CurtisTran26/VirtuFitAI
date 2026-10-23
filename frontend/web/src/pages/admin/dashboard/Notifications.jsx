import React, { useState } from 'react';

const initialNotifications = [
  { id: 1, icon: '📦', title: 'Đơn hàng mới #VF-1284 đã thanh toán qua VNPay', time: '5 phút trước', read: false },
  { id: 2, icon: '⚠️', title: 'Sản phẩm “Áo sơ mi linen” sắp hết hàng (còn 4)', time: '32 phút trước', read: false },
  { id: 3, icon: '👜', title: 'Tác vụ thử đồ AI thất bại (timeout) – đã tự thử lại', time: '1 giờ trước', read: false },
  { id: 4, icon: '👤', title: 'Tài khoản nhân viên mới được tạo: Ngô Thanh Vy', time: 'Hôm qua', read: true },
  { id: 5, icon: '📈', title: 'Doanh thu tuần đạt 118 triệu, tăng 12% so với tuần trước', time: '2 ngày trước', read: true },
];

const Notifications = ({ isHidden, onUnreadCountChange }) => {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [filter, setFilter] = useState('all');
  const unreadCount = notifications.filter((notification) => !notification.read).length;
  const visibleNotifications = notifications.filter((notification) => filter === 'all' || !notification.read);

  const updateNotifications = (nextNotifications) => {
    setNotifications(nextNotifications);
    onUnreadCountChange(nextNotifications.filter((notification) => !notification.read).length);
  };

  const markOneRead = (id) => {
    updateNotifications(notifications.map((notification) => notification.id === id ? { ...notification, read: true } : notification));
  };

  const markAllRead = () => updateNotifications(notifications.map((notification) => ({ ...notification, read: true })));

  return (
    <div className={`space-y-4 ${isHidden ? 'hidden' : ''}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Thông báo</h1>
        <button type="button" onClick={markAllRead} disabled={unreadCount === 0} className="rounded-lg border border-[#262b45] bg-[#181c30] px-3 py-2 text-xs font-semibold text-[#c5c9da] hover:bg-[#262b45] disabled:opacity-50">✓ Đánh dấu tất cả đã đọc</button>
      </div>

      <div className="flex gap-2" role="group" aria-label="Lọc thông báo">
        {[
          { id: 'all', label: 'Tất cả' },
          { id: 'unread', label: `Chưa đọc${unreadCount ? ` (${unreadCount})` : ''}` },
        ].map((item) => (
          <button key={item.id} type="button" aria-pressed={filter === item.id} onClick={() => setFilter(item.id)} className={`rounded-lg border px-3 py-2 text-xs font-semibold ${filter === item.id ? 'border-[#5b4bff] bg-[#26235a] text-[#8b82ff]' : 'border-[#262b45] bg-[#181c30] text-[#9aa2c0] hover:text-white'}`}>{item.label}</button>
        ))}
      </div>

      <div className="overflow-hidden rounded-xl border border-[#262b45] bg-[#181c30]">
        {visibleNotifications.map((notification) => (
          <button key={notification.id} type="button" onClick={() => markOneRead(notification.id)} aria-label={`${notification.read ? 'Đã đọc' : 'Chưa đọc'}: ${notification.title}`} className={`flex w-full items-center gap-3 border-b border-[#262b45] px-4 py-3 text-left last:border-0 hover:bg-[#26235a]/50 ${notification.read ? '' : 'bg-[#26235a]/50'}`}>
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#0f2e24] text-sm" aria-hidden="true">{notification.icon}</span>
            <span className="min-w-0 flex-1">
              <span className="block text-xs font-semibold">{notification.title}</span>
              <span className="mt-1 block text-[10px] text-[#9aa2c0]">{notification.time}</span>
            </span>
            {!notification.read && <span className="h-2 w-2 shrink-0 rounded-full bg-[#5b4bff]" aria-label="Chưa đọc" />}
          </button>
        ))}
        {visibleNotifications.length === 0 && <p className="px-4 py-10 text-center text-sm text-[#9aa2c0]">Bạn đã đọc hết thông báo.</p>}
      </div>
    </div>
  );
};

export default Notifications;