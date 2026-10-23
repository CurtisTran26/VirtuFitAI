import React, { useState } from 'react';

const initialNotifications = [
  { id: 1, icon: '📦', iconStyle: 'bg-[#0f2e24] text-[#12a66a]', title: 'Đơn mới #VF-1284 cần chuẩn bị (3 sản phẩm)', time: '5 phút trước', read: false },
  { id: 2, icon: '⚠️', iconStyle: 'bg-[#3a2e12] text-[#e8930c]', title: 'Áo sơ mi linen (Trắng/L) sắp hết hàng – còn 4', time: '22 phút trước', read: false },
  { id: 3, icon: '↩️', iconStyle: 'bg-[#17284a] text-[#60a5fa]', title: 'Yêu cầu trả hàng RT-0232 đang chờ tiếp nhận', time: '1 giờ trước', read: false },
  { id: 4, icon: '✂️', iconStyle: 'bg-[#12383a] text-[#0f9d8a]', title: 'Đơn thiết kế riêng CD-0045 đã được khách xác nhận báo giá', time: '4 giờ trước', read: true },
  { id: 5, icon: '📦', iconStyle: 'bg-[#12383a] text-[#0f9d8a]', title: 'Đơn #VF-1281 đã bàn giao vận chuyển', time: 'Hôm qua', read: true },
];

const Notifications = ({ isHidden, onUnreadCountChange }) => {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [filter, setFilter] = useState('all');
  const unreadCount = notifications.filter((notification) => !notification.read).length;
  const visibleNotifications = notifications.filter((notification) => filter === 'all' || !notification.read);

  const markNotificationRead = (notificationId) => {
    const notification = notifications.find((item) => item.id === notificationId);
    if (!notification || notification.read) return;

    const updatedNotifications = notifications.map((item) => (
      item.id === notificationId ? { ...item, read: true } : item
    ));
    setNotifications(updatedNotifications);
    onUnreadCountChange(updatedNotifications.filter((item) => !item.read).length);
  };

  const markAllRead = () => {
    if (unreadCount === 0) return;
    setNotifications((currentNotifications) => currentNotifications.map((notification) => ({ ...notification, read: true })));
    onUnreadCountChange(0);
  };

  return (
    <div className={`space-y-4 ${isHidden ? 'hidden' : ''}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Thông báo</h1>
        <button
          type="button"
          onClick={markAllRead}
          disabled={unreadCount === 0}
          className="rounded-lg border border-[#24383b] bg-[#152427] px-3 py-2 text-xs font-semibold text-[#c5d2d2] transition-colors hover:bg-[#24383b] disabled:cursor-not-allowed disabled:opacity-50"
        >
          ✓ Đánh dấu tất cả đã đọc
        </button>
      </div>

      <div className="flex gap-2" role="group" aria-label="Lọc thông báo">
        <button
          type="button"
          aria-pressed={filter === 'all'}
          onClick={() => setFilter('all')}
          className={`rounded-lg border px-3 py-2 text-xs font-semibold transition-colors ${filter === 'all' ? 'border-[#0f9d8a] bg-[#12383a] text-[#0f9d8a]' : 'border-[#24383b] bg-[#152427] text-[#92a9ad] hover:text-white'}`}
        >
          Tất cả
        </button>
        <button
          type="button"
          aria-pressed={filter === 'unread'}
          onClick={() => setFilter('unread')}
          className={`rounded-lg border px-3 py-2 text-xs font-semibold transition-colors ${filter === 'unread' ? 'border-[#0f9d8a] bg-[#12383a] text-[#0f9d8a]' : 'border-[#24383b] bg-[#152427] text-[#92a9ad] hover:text-white'}`}
        >
          Chưa đọc{unreadCount > 0 ? ` (${unreadCount})` : ''}
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-[#24383b] bg-[#152427]">
        {visibleNotifications.map((notification) => (
          <button
            key={notification.id}
            type="button"
            onClick={() => markNotificationRead(notification.id)}
            aria-label={`${notification.read ? 'Đã đọc' : 'Chưa đọc'}: ${notification.title}`}
            className={`flex w-full items-center gap-3 border-b border-[#24383b] px-4 py-3 text-left transition-colors last:border-0 hover:bg-[#12383a]/50 ${notification.read ? 'bg-[#152427]' : 'bg-[#12383a]/70'}`}
          >
            <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm ${notification.iconStyle}`} aria-hidden="true">
              {notification.icon}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-xs font-semibold text-[#e8f2f1]">{notification.title}</span>
              <span className="mt-1 block text-[10px] text-[#92a9ad]">{notification.time}</span>
            </span>
            {!notification.read && <span className="h-2 w-2 shrink-0 rounded-full bg-[#0f9d8a]" aria-label="Chưa đọc" />}
          </button>
        ))}
        {visibleNotifications.length === 0 && (
          <p className="px-4 py-10 text-center text-sm text-[#92a9ad]">Bạn đã đọc hết thông báo.</p>
        )}
      </div>
    </div>
  );
};

export default Notifications;