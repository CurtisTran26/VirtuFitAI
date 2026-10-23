import React, { useState } from 'react';

const productionStages = [
  'Đã tiếp nhận',
  'Chuẩn bị vật liệu',
  'Đang may',
  'Hoàn thiện & QC',
  'Đang giao',
];

const initialCustomOrders = [
  {
    id: 'CD-0045',
    customer: 'Nguyễn Minh Anh',
    detail: 'Áo blazer oversize, vải tweed xám',
    designer: 'Ngô Thanh Vy',
    deadline: '12/10/2026',
    stage: 0,
  },
  {
    id: 'CD-0044',
    customer: 'Trần Bảo Ngọc',
    detail: 'Đầm dạ hội lụa đỏ đô, tay bồng',
    designer: 'Ngô Thanh Vy',
    deadline: '18/10/2026',
    stage: 2,
  },
  {
    id: 'CD-0042',
    customer: 'Lê Hoàng Nam',
    detail: 'Sơ mi lanh may đo, cổ Mandarin',
    designer: 'Ngô Thanh Vy',
    deadline: '06/10/2026',
    stage: 4,
  },
];

const CustomOrderProgress = ({ currentStage }) => (
  <div className="relative px-2">
    <div className="absolute left-[10%] right-[10%] top-[7px] h-0.5 bg-[#24383b]">
      <div
        className="h-full bg-[#0f9d8a] transition-all"
        style={{ width: `${(currentStage / (productionStages.length - 1)) * 100}%` }}
      />
    </div>
    <div className="relative grid grid-cols-5">
      {productionStages.map((stage, index) => (
        <div key={stage} className="flex min-w-0 flex-col items-center gap-2 text-center">
          <span className={`z-10 h-4 w-4 rounded-full border-2 ${index <= currentStage ? 'border-[#0f9d8a] bg-[#0f9d8a]' : 'border-[#34494b] bg-[#152427]'}`} />
          <span className={`text-[9px] leading-tight sm:text-[10px] ${index <= currentStage ? 'text-[#d7e4e2]' : 'text-[#718486]'}`}>
            {stage}
          </span>
        </div>
      ))}
    </div>
  </div>
);

const CustomOrders = () => {
  const [orders, setOrders] = useState(initialCustomOrders);
  const [selectedStages, setSelectedStages] = useState(() => Object.fromEntries(
    initialCustomOrders.map((order) => [order.id, String(order.stage)])
  ));

  const handleStageChange = (orderId, stage) => {
    setSelectedStages((currentStages) => ({ ...currentStages, [orderId]: stage }));
  };

  const handleUpdate = (orderId) => {
    const nextStage = Number(selectedStages[orderId]);
    setOrders((currentOrders) => currentOrders.map((order) => (
      order.id === orderId ? { ...order, stage: nextStage } : order
    )));
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold">Đơn thiết kế riêng</h1>
      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        {orders.map((order) => (
          <article key={order.id} className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold">{order.id}</h2>
                <span className="rounded-full bg-[#12383a] px-2.5 py-1 text-[10px] font-bold text-[#0f9d8a]">
                  {productionStages[order.stage]}
                </span>
              </div>
              <p className="text-[10px] text-[#92a9ad]">Hẹn: {order.deadline}</p>
            </div>

            <div className="mt-2">
              <p className="text-xs font-semibold">{order.customer}</p>
              <p className="text-xs leading-relaxed text-[#92a9ad]">{order.detail}</p>
              <p className="text-xs text-[#92a9ad]">Designer: {order.designer}</p>
            </div>

            <div className="mt-4">
              <CustomOrderProgress currentStage={order.stage} />
            </div>

            <div className="mt-3 flex gap-2">
              <select
                aria-label={`Cập nhật tiến độ ${order.id}`}
                value={selectedStages[order.id]}
                onChange={(event) => handleStageChange(order.id, event.target.value)}
                className="min-w-0 flex-1 rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2 text-xs text-white outline-none focus:border-[#0f9d8a]"
              >
                {productionStages.map((stage, index) => (
                  <option key={stage} value={index}>{stage}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => handleUpdate(order.id)}
                disabled={Number(selectedStages[order.id]) === order.stage}
                className="rounded-lg bg-[#0f9d8a] px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c] disabled:cursor-not-allowed disabled:opacity-50"
              >
                Cập nhật
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default CustomOrders;