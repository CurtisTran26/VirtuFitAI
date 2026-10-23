import React, { useState } from 'react';

const orderStatuses = ['Chờ chuẩn bị', 'Đang đóng gói', 'Đã bàn giao vận chuyển'];

const initialOrders = [
  {
    id: '#VF-1284',
    customer: 'Nguyễn Minh Anh',
    payment: 'VNPay – Đã thanh toán',
    status: 'Chờ chuẩn bị',
    items: [
      { name: 'Áo sơ mi linen', variant: 'Trắng / M', quantity: 2 },
      { name: 'Quần jeans slim', variant: 'Xanh navy / L', quantity: 1 },
    ],
  },
  {
    id: '#VF-1283',
    customer: 'Trần Bảo Ngọc',
    payment: 'COD',
    status: 'Chờ chuẩn bị',
    items: [{ name: 'Đầm midi hoa', variant: 'Đỏ đô / M', quantity: 1 }],
  },
  {
    id: '#VF-1281',
    customer: 'Phạm Thu Hà',
    payment: 'VNPay – Đã thanh toán',
    status: 'Đang đóng gói',
    items: [
      { name: 'Áo khoác bomber', variant: 'Đen / M', quantity: 1 },
      { name: 'Váy xếp ly', variant: 'Be / S', quantity: 1 },
    ],
  },
  {
    id: '#VF-1277',
    customer: 'Võ Quốc Đạt',
    payment: 'COD',
    status: 'Đã bàn giao vận chuyển',
    items: [{ name: 'Áo sơ mi linen', variant: 'Trắng / L', quantity: 1 }],
  },
];

const statusStyles = {
  'Chờ chuẩn bị': 'bg-[#3a2e12] text-[#e8930c]',
  'Đang đóng gói': 'bg-[#17284a] text-[#60a5fa]',
  'Đã bàn giao vận chuyển': 'bg-[#0f2e24] text-[#12a66a]',
};

const OrderProgress = ({ status }) => {
  const activeStep = orderStatuses.indexOf(status);

  return (
    <div className="relative mt-6 grid grid-cols-3">
      <div className="absolute left-[16.67%] right-[16.67%] top-[7px] h-0.5 bg-[#24383b]">
        <div
          className="h-full bg-[#0f9d8a] transition-all"
          style={{ width: `${(activeStep / (orderStatuses.length - 1)) * 100}%` }}
        />
      </div>
      {orderStatuses.map((step, index) => (
        <div key={step} className="relative flex flex-col items-center gap-2 text-center">
          <span className={`z-10 h-4 w-4 rounded-full border-2 ${index <= activeStep ? 'border-[#0f9d8a] bg-[#0f9d8a]' : 'border-[#34494b] bg-[#152427]'}`} />
          <span className={`text-[10px] ${index <= activeStep ? 'text-[#d7e4e2]' : 'text-[#718486]'}`}>{step}</span>
        </div>
      ))}
    </div>
  );
};

const Orders = () => {
  const [orders, setOrders] = useState(initialOrders);
  const [activeFilter, setActiveFilter] = useState('Tất cả');
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  const selectedOrder = orders.find((order) => order.id === selectedOrderId);
  const filters = ['Tất cả', ...orderStatuses];
  const visibleOrders = orders.filter((order) => activeFilter === 'Tất cả' || order.status === activeFilter);
  const statusCounts = orderStatuses.map((status) => ({
    label: status,
    count: orders.filter((order) => order.status === status).length,
  }));

  const advanceOrder = () => {
    if (!selectedOrder) return;
    const currentStep = orderStatuses.indexOf(selectedOrder.status);
    if (currentStep < 0 || currentStep === orderStatuses.length - 1) return;

    const nextStatus = orderStatuses[currentStep + 1];
    setOrders((currentOrders) => currentOrders.map((order) => (
      order.id === selectedOrder.id ? { ...order, status: nextStatus } : order
    )));
  };

  return (
    <>
      <div className="space-y-4">
        <h1 className="text-lg font-bold">Đơn cần chuẩn bị</h1>

        <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
          {statusCounts.map(({ label, count }) => (
            <div key={label} className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
              <p className="text-xs text-[#92a9ad]">{label}</p>
              <p className="mt-1 text-xl font-bold tabular-nums">{count}</p>
            </div>
          ))}
          <div className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
            <p className="text-xs text-[#92a9ad]">Tổng đơn</p>
            <p className="mt-1 text-xl font-bold tabular-nums">{orders.length}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2" role="group" aria-label="Lọc đơn hàng">
          {filters.map((filter) => (
            <button
              key={filter}
              type="button"
              onClick={() => setActiveFilter(filter)}
              aria-pressed={activeFilter === filter}
              className={`rounded-lg border px-3 py-2 text-xs font-semibold transition-colors ${activeFilter === filter ? 'border-[#0f9d8a] bg-[#12383a] text-[#0f9d8a]' : 'border-[#24383b] bg-[#152427] text-[#92a9ad] hover:text-white'}`}
            >
              {filter}
            </button>
          ))}
        </div>

        <div className="overflow-x-auto rounded-xl border border-[#24383b] bg-[#152427]">
          <table className="w-full min-w-[760px] text-left">
            <thead>
              <tr className="border-b border-[#24383b] text-xs text-[#92a9ad]">
                <th className="px-4 py-3 font-semibold">Mã đơn</th>
                <th className="px-4 py-3 font-semibold">Khách hàng</th>
                <th className="px-4 py-3 font-semibold">Số SP</th>
                <th className="px-4 py-3 font-semibold">Thanh toán</th>
                <th className="px-4 py-3 font-semibold">Trạng thái</th>
                <th className="px-4 py-3" aria-label="Thao tác"></th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {visibleOrders.map((order) => (
                <tr key={order.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30">
                  <td className="px-4 py-3 font-bold">{order.id}</td>
                  <td className="px-4 py-3">{order.customer}</td>
                  <td className="px-4 py-3 tabular-nums">{order.items.reduce((total, item) => total + item.quantity, 0)}</td>
                  <td className="px-4 py-3">{order.payment}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold ${statusStyles[order.status]}`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => setSelectedOrderId(order.id)}
                      className="rounded-lg bg-[#0f9d8a] px-3 py-1.5 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c]"
                    >
                      Chi tiết
                    </button>
                  </td>
                </tr>
              ))}
              {visibleOrders.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-4 py-10 text-center text-sm text-[#92a9ad]">Không có đơn hàng ở trạng thái này.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedOrder && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setSelectedOrderId(null);
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="order-detail-title"
            className="w-full max-w-md rounded-xl border border-[#24383b] bg-[#152427] p-5 shadow-2xl"
          >
            <h2 id="order-detail-title" className="text-base font-bold">Đơn {selectedOrder.id}</h2>
            <p className="mt-1 text-xs text-[#92a9ad]">{selectedOrder.customer} · {selectedOrder.payment}</p>

            <div className="mt-4 divide-y divide-[#24383b]">
              {selectedOrder.items.map((item) => (
                <div key={`${item.name}-${item.variant}`} className="flex items-start justify-between gap-4 py-3 text-xs">
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    <p className="mt-0.5 text-[#92a9ad]">{item.variant}</p>
                  </div>
                  <span className="whitespace-nowrap font-semibold">× {item.quantity}</span>
                </div>
              ))}
            </div>

            <OrderProgress status={selectedOrder.status} />

            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedOrderId(null)}
                className="rounded-lg border border-[#24383b] px-4 py-2 text-xs font-bold text-[#c5d2d2] transition-colors hover:bg-[#24383b]"
              >
                Đóng
              </button>
              {selectedOrder.status === 'Chờ chuẩn bị' && (
                <button
                  type="button"
                  onClick={advanceOrder}
                  className="rounded-lg bg-[#0f9d8a] px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c]"
                >
                  Bắt đầu đóng gói
                </button>
              )}
              {selectedOrder.status === 'Đang đóng gói' && (
                <button
                  type="button"
                  onClick={advanceOrder}
                  className="rounded-lg bg-[#0f9d8a] px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c]"
                >
                  Xác nhận bàn giao vận chuyển
                </button>
              )}
            </div>
          </section>
        </div>
      )}
    </>
  );
};

export default Orders;