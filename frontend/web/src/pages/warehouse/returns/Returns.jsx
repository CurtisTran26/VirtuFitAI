import React, { useState } from 'react';

const initialReturns = [
  { id: 'RT-0231', order: '#VF-1210', product: 'Áo sơ mi linen (Trắng/L)', reason: 'Không vừa size', status: 'Chờ tiếp nhận' },
  { id: 'RT-0232', order: '#VF-1219', product: 'Đầm midi hoa (Đỏ đô/M)', reason: 'Sản phẩm lỗi chỉ', status: 'Chờ tiếp nhận' },
  { id: 'RT-0229', order: '#VF-1198', product: 'Quần jeans slim (Xanh navy/L)', reason: 'Đổi ý', status: 'Đã nhập kho' },
  { id: 'RT-0227', order: '#VF-1185', product: 'Váy xếp ly (Be/S)', reason: 'Giao nhầm màu', status: 'Không đạt – từ chối' },
];

const statusStyles = {
  'Chờ tiếp nhận': 'bg-[#3a2e12] text-[#e8930c]',
  'Đã nhập kho': 'bg-[#0f2e24] text-[#12a66a]',
  'Không đạt – từ chối': 'bg-[#3a1a1e] text-[#e5484d]',
};

const Returns = () => {
  const [returns, setReturns] = useState(initialReturns);
  const [selectedReturn, setSelectedReturn] = useState(null);
  const [inspectionResult, setInspectionResult] = useState('accepted');
  const [note, setNote] = useState('');

  const openInspection = (returnItem) => {
    setSelectedReturn(returnItem);
    setInspectionResult('accepted');
    setNote('');
  };

  const closeInspection = () => {
    setSelectedReturn(null);
  };

  const handleInspectionSubmit = (event) => {
    event.preventDefault();
    if (!selectedReturn) return;

    const nextStatus = inspectionResult === 'accepted' ? 'Đã nhập kho' : 'Không đạt – từ chối';
    setReturns((currentReturns) => currentReturns.map((returnItem) => (
      returnItem.id === selectedReturn.id
        ? { ...returnItem, status: nextStatus, inspectionNote: note.trim() }
        : returnItem
    )));
    closeInspection();
  };

  return (
    <>
      <div className="space-y-4">
        <h1 className="text-lg font-bold">Tiếp nhận &amp; kiểm tra hàng trả</h1>
        <div className="bg-[#152427] border border-[#24383b] rounded-xl overflow-x-auto">
          <table className="w-full min-w-[760px] text-left">
            <thead>
              <tr className="border-b border-[#24383b] text-[#92a9ad] text-xs">
                <th className="px-4 py-3 font-semibold">Mã trả</th>
                <th className="px-4 py-3 font-semibold">Đơn gốc</th>
                <th className="px-4 py-3 font-semibold">Sản phẩm</th>
                <th className="px-4 py-3 font-semibold">Lý do</th>
                <th className="px-4 py-3 font-semibold">Trạng thái</th>
                <th className="px-4 py-3" aria-label="Thao tác"></th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {returns.map((returnItem) => (
                <tr key={returnItem.id} className="border-b border-[#24383b] last:border-0 hover:bg-[#12383a]/30 transition-colors">
                  <td className="px-4 py-3 font-bold">{returnItem.id}</td>
                  <td className="px-4 py-3">{returnItem.order}</td>
                  <td className="px-4 py-3">{returnItem.product}</td>
                  <td className="px-4 py-3">
                    {returnItem.reason}
                    {returnItem.inspectionNote && (
                      <p className="mt-1 max-w-[220px] truncate text-xs text-[#92a9ad]" title={returnItem.inspectionNote}>
                        Ghi chú: {returnItem.inspectionNote}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold ${statusStyles[returnItem.status]}`}>
                      {returnItem.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {returnItem.status === 'Chờ tiếp nhận' && (
                      <button
                        type="button"
                        onClick={() => openInspection(returnItem)}
                        className="whitespace-nowrap rounded-lg bg-[#0f9d8a] px-3 py-1.5 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c]"
                      >
                        Kiểm tra
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedReturn && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeInspection();
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="return-inspection-title"
            className="w-full max-w-md rounded-xl border border-[#24383b] bg-[#152427] p-5 shadow-2xl"
          >
            <h2 id="return-inspection-title" className="text-base font-bold">
              Kiểm tra hàng trả {selectedReturn.id}
            </h2>
            <p className="mt-1 text-xs text-[#92a9ad]">
              {selectedReturn.product} · Lý do: {selectedReturn.reason}
            </p>

            <form onSubmit={handleInspectionSubmit} className="mt-4 space-y-3">
              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-[#c5d2d2]">Kết quả kiểm tra</span>
                <select
                  value={inspectionResult}
                  onChange={(event) => setInspectionResult(event.target.value)}
                  className="w-full rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none focus:border-[#0f9d8a]"
                >
                  <option value="accepted">Đạt – nhập lại kho</option>
                  <option value="rejected">Không đạt – từ chối</option>
                </select>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-[#c5d2d2]">Ghi chú</span>
                <textarea
                  rows="3"
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  placeholder="Tình trạng sản phẩm, tem mác..."
                  className="w-full resize-y rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none placeholder:text-[#647779] focus:border-[#0f9d8a]"
                />
              </label>

              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={closeInspection}
                  className="rounded-lg border border-[#24383b] px-4 py-2 text-xs font-bold text-[#c5d2d2] transition-colors hover:bg-[#24383b]"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-[#0f9d8a] px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-[#0b7a6c]"
                >
                  Xác nhận kiểm tra
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  );
};

export default Returns;