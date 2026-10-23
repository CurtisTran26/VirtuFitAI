import React, { useMemo, useState } from 'react';

const initialReports = [
  { date: '2026-09-30', orders: 58, online: 15200000, offline: 6300000, refunds: 0 },
  { date: '2026-09-29', orders: 70, online: 17860000, offline: 8050000, refunds: 3 },
  { date: '2026-09-28', orders: 82, online: 20520000, offline: 9800000, refunds: 1 },
  { date: '2026-09-27', orders: 79, online: 23180000, offline: 6300000, refunds: 4 },
  { date: '2026-09-26', orders: 68, online: 17100000, offline: 8050000, refunds: 2 },
  { date: '2026-09-25', orders: 80, online: 19760000, offline: 9800000, refunds: 0 },
  { date: '2026-09-24', orders: 77, online: 22420000, offline: 6300000, refunds: 3 },
  { date: '2026-09-23', orders: 66, online: 16340000, offline: 8050000, refunds: 1 },
  { date: '2026-09-22', orders: 78, online: 19000000, offline: 9800000, refunds: 4 },
  { date: '2026-09-21', orders: 75, online: 21660000, offline: 6300000, refunds: 2 },
];

const formatMoney = (amount) => `${new Intl.NumberFormat('vi-VN').format(amount)}₫`;
const formatDate = (date) => new Date(`${date}T00:00:00`).toLocaleDateString('vi-VN');

const RevenueReports = () => {
  const [startDate, setStartDate] = useState('2026-09-01');
  const [endDate, setEndDate] = useState('2026-09-30');
  const [channel, setChannel] = useState('all');
  const [appliedFilters, setAppliedFilters] = useState({ startDate: '2026-09-01', endDate: '2026-09-30', channel: 'all' });
  const [isExportOpen, setExportOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');
  const [exportScope, setExportScope] = useState('revenue');
  const [filterError, setFilterError] = useState('');

  const reports = useMemo(() => initialReports
    .filter((report) => report.date >= appliedFilters.startDate && report.date <= appliedFilters.endDate)
    .map((report) => {
      const online = appliedFilters.channel === 'offline' ? 0 : report.online;
      const offline = appliedFilters.channel === 'online' ? 0 : report.offline;
      return { ...report, online, offline, revenue: online + offline };
    }), [appliedFilters]);

  const applyFilters = (event) => {
    event.preventDefault();
    if (startDate && endDate && startDate > endDate) {
      setFilterError('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.');
      return;
    }
    setFilterError('');
    setAppliedFilters({ startDate, endDate, channel });
  };

  const exportReport = () => {
    const rows = exportScope === 'revenue'
      ? [['Ngày', 'Số đơn', 'Online', 'Tại quầy', 'Hoàn/hủy', 'Doanh thu'], ...reports.map((report) => [formatDate(report.date), report.orders, report.online, report.offline, report.refunds, report.revenue])]
      : [['Ngày', 'Kênh bán', 'Số đơn', 'Doanh thu'], ...reports.flatMap((report) => [
        [formatDate(report.date), 'Online', report.orders, report.online],
        [formatDate(report.date), 'Tại quầy', report.orders, report.offline],
      ])];

    const content = exportFormat === 'json'
      ? JSON.stringify(rows.slice(1).map((row) => Object.fromEntries(rows[0].map((heading, index) => [heading, row[index]]))), null, 2)
      : `\uFEFF${rows.map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\r\n')}`;
    const mimeType = exportFormat === 'json' ? 'application/json' : 'text/csv;charset=utf-8';
    const extension = exportFormat === 'json' ? 'json' : 'csv';
    const downloadUrl = URL.createObjectURL(new Blob([content], { type: mimeType }));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `bao-cao-doanh-thu.${extension}`;
    link.click();
    URL.revokeObjectURL(downloadUrl);
    setExportOpen(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Báo cáo doanh thu</h1>
        <button type="button" onClick={() => setExportOpen(true)} className="rounded-lg bg-[#5b4bff] px-4 py-2 text-xs font-bold text-white hover:bg-[#4a3ecc]">⇩ Xuất báo cáo</button>
      </div>

      <form onSubmit={applyFilters} className="flex flex-wrap items-end gap-3 rounded-xl border border-[#262b45] bg-[#181c30] p-4">
        <label className="min-w-[145px] flex-1 text-xs font-semibold text-[#9aa2c0]">
          Từ ngày
          <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} className="mt-2 w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]" />
        </label>
        <label className="min-w-[145px] flex-1 text-xs font-semibold text-[#9aa2c0]">
          Đến ngày
          <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} className="mt-2 w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]" />
        </label>
        <label className="min-w-[170px] flex-1 text-xs font-semibold text-[#9aa2c0]">
          Kênh bán
          <select value={channel} onChange={(event) => setChannel(event.target.value)} className="mt-2 w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]">
            <option value="all">Tất cả</option>
            <option value="online">Online (VNPay/COD)</option>
            <option value="offline">Tại quầy (POS)</option>
          </select>
        </label>
        <button type="submit" className="rounded-lg bg-[#5b4bff] px-5 py-2.5 text-sm font-bold text-white hover:bg-[#4a3ecc]">Áp dụng</button>
        {filterError && <p role="alert" className="w-full text-xs text-[#e5484d]">{filterError}</p>}
      </form>

      <div className="overflow-x-auto rounded-xl border border-[#262b45] bg-[#181c30]">
        <table className="w-full min-w-[700px] text-left">
          <thead>
            <tr className="border-b border-[#262b45] text-xs text-[#9aa2c0]">
              {['Ngày', 'Số đơn', 'Online', 'Tại quầy', 'Hoàn/hủy', 'Doanh thu'].map((heading) => <th key={heading} className="px-4 py-3 font-semibold">{heading}</th>)}
            </tr>
          </thead>
          <tbody className="text-xs">
            {reports.map((report) => (
              <tr key={report.date} className="border-b border-[#262b45] last:border-0 hover:bg-[#20243a]">
                <td className="px-4 py-3">{formatDate(report.date)}</td>
                <td className="px-4 py-3">{report.orders}</td>
                <td className="px-4 py-3">{formatMoney(report.online)}</td>
                <td className="px-4 py-3">{formatMoney(report.offline)}</td>
                <td className="px-4 py-3">{report.refunds}</td>
                <td className="px-4 py-3 font-bold">{formatMoney(report.revenue)}</td>
              </tr>
            ))}
            {reports.length === 0 && <tr><td colSpan="6" className="px-4 py-10 text-center text-[#9aa2c0]">Không có dữ liệu trong khoảng thời gian đã chọn.</td></tr>}
          </tbody>
        </table>
      </div>

      {isExportOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) setExportOpen(false); }}>
          <section role="dialog" aria-modal="true" aria-labelledby="export-report-title" className="w-full max-w-md rounded-xl border border-[#262b45] bg-[#181c30] p-5 shadow-2xl">
            <h2 id="export-report-title" className="font-bold">Xuất báo cáo</h2>
            <p className="mt-1 text-xs text-[#9aa2c0]">Chọn định dạng và phạm vi dữ liệu.</p>
            <label className="mt-4 block text-xs font-semibold text-[#9aa2c0]">Định dạng
              <select value={exportFormat} onChange={(event) => setExportFormat(event.target.value)} className="mt-2 w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]">
                <option value="csv">CSV (mở bằng Excel)</option>
                <option value="json">JSON</option>
              </select>
            </label>
            <label className="mt-3 block text-xs font-semibold text-[#9aa2c0]">Nội dung
              <select value={exportScope} onChange={(event) => setExportScope(event.target.value)} className="mt-2 w-full rounded-lg border border-[#262b45] bg-[#0f1220] px-3 py-2.5 text-sm text-white outline-none focus:border-[#5b4bff]">
                <option value="revenue">Doanh thu theo ngày</option>
                <option value="channels">Chi tiết theo kênh bán</option>
              </select>
            </label>
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" onClick={() => setExportOpen(false)} className="rounded-lg border border-[#262b45] px-4 py-2 text-xs font-bold text-[#9aa2c0] hover:bg-[#262b45]">Hủy</button>
              <button type="button" onClick={exportReport} className="rounded-lg bg-[#5b4bff] px-4 py-2 text-xs font-bold text-white hover:bg-[#4a3ecc]">Xuất file</button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
};

export default RevenueReports;