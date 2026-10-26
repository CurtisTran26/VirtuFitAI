import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../utils/apiClient';

const inputClass = 'w-full rounded-lg border border-[#24383b] bg-[#0e1a1c] px-3 py-2.5 text-sm text-white outline-none focus:border-[#0f9d8a]';
const buttonClass = 'rounded-lg bg-[#0f9d8a] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#0b7a6c] disabled:cursor-not-allowed disabled:opacity-50';
const dimensions = [
  ['height_cm', 'Chiều cao (cm)'],
  ['weight_kg', 'Cân nặng (kg)'],
  ['chest_cm', 'Ngực (cm)'],
  ['waist_cm', 'Eo (cm)'],
];
const emptyMeasurements = (sizes) => sizes.map(({ name }) => ({ size: name, height_cm: '', weight_kg: '', chest_cm: '', waist_cm: '' }));

const Catalog = () => {
  const [tab, setTab] = useState('categories');
  const [categories, setCategories] = useState([]);
  const [charts, setCharts] = useState([]);
  const [colors, setColors] = useState([]);
  const [sizes, setSizes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [categoryName, setCategoryName] = useState('');
  const [editingCategory, setEditingCategory] = useState(null);
  const [colorForm, setColorForm] = useState({ name: '', hex_color: '#ffffff' });
  const [sizeName, setSizeName] = useState('');
  const [chartForm, setChartForm] = useState({ category_id: '', name: '', measurements: [] });
  const [selectedChartId, setSelectedChartId] = useState('');
  const [savingChart, setSavingChart] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [categoryResult, chartResult, optionResult] = await Promise.all([
        apiClient.get('categories?page=1&limit=100'),
        apiClient.get('size-charts'),
        apiClient.get('catalog-options'),
      ]);
      const nextCategories = categoryResult.items || [];
      const nextCharts = chartResult.items || [];
      const nextSizes = optionResult.sizes || [];
      setCategories(nextCategories);
      setCharts(nextCharts);
      setColors(optionResult.colors || []);
      setSizes(nextSizes);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    if (loading || chartForm.category_id) return;
    const category = categories.find((item) => item.is_active);
    if (!category) return;
    const chart = charts.find((item) => item.category_id === category.id);
    setSelectedChartId(chart?.id || '');
    setChartForm(chart
      ? { category_id: chart.category_id, name: chart.name, measurements: chart.measurements || [] }
      : { category_id: category.id, name: '', measurements: emptyMeasurements(sizes) });
  }, [loading, chartForm.category_id, categories, charts, sizes]);

  const submitCategory = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const body = {
        name: categoryName.trim(),
        description: editingCategory?.description || '',
        is_active: true,
      };
      if (editingCategory) await apiClient.patch(`categories/${editingCategory.id}`, body);
      else await apiClient.post('categories', body);
      setCategoryName('');
      setEditingCategory(null);
      await loadData();
    } catch (submitError) { setError(submitError.message); }
  };

  const archiveCategory = async (category) => {
    if (!window.confirm(`Ẩn danh mục “${category.name}”?`)) return;
    setError('');
    try { await apiClient.delete(`categories/${category.id}`); await loadData(); }
    catch (deleteError) { setError(deleteError.message); }
  };

  const submitColor = async (event) => {
    event.preventDefault();
    setError('');
    try {
      await apiClient.post('catalog-options/colors', { name: colorForm.name.trim(), hex_color: colorForm.hex_color });
      setColorForm({ name: '', hex_color: '#ffffff' });
      await loadData();
    } catch (submitError) { setError(submitError.message); }
  };

  const deleteColor = async (color) => {
    if (!window.confirm(`Xóa màu “${color.name}”?`)) return;
    setError('');
    try { await apiClient.delete(`catalog-options/colors/${color.id}`); await loadData(); }
    catch (deleteError) { setError(deleteError.message); }
  };

  const submitSize = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const result = await apiClient.post('catalog-options/sizes', { name: sizeName.trim() });
      setSizeName('');
      setChartForm((current) => current.measurements.some((row) => row.size === result.name)
        ? current
        : { ...current, measurements: [...current.measurements, { size: result.name, height_cm: '', weight_kg: '', chest_cm: '', waist_cm: '' }] });
      await loadData();
    } catch (submitError) { setError(submitError.message); }
  };

  const deleteSize = async (size) => {
    if (!window.confirm(`Xóa size “${size.name}” khỏi danh sách dùng chung?`)) return;
    setError('');
    try { await apiClient.delete(`catalog-options/sizes/${size.id}`); await loadData(); }
    catch (deleteError) { setError(deleteError.message); }
  };

  const selectChart = (chartId, categoryId = chartForm.category_id) => {
    setSelectedChartId(chartId);
    const chart = charts.find((item) => item.id === chartId);
    if (chart) {
      setChartForm({ category_id: chart.category_id, name: chart.name, measurements: chart.measurements || [] });
    } else {
      setChartForm({ category_id: categoryId, name: '', measurements: emptyMeasurements(sizes) });
    }
  };

  const selectChartCategory = (categoryId) => {
    const chart = charts.find((item) => item.category_id === categoryId);
    selectChart(chart?.id || '', categoryId);
  };

  const updateMeasurement = (rowIndex, field, value) => {
    setChartForm((current) => ({
      ...current,
      measurements: current.measurements.map((row, index) => index === rowIndex ? { ...row, [field]: value } : row),
    }));
  };

  const saveChart = async (event) => {
    event.preventDefault();
    setError('');
    setSavingChart(true);
    try {
      const body = {
        category_id: chartForm.category_id,
        name: chartForm.name.trim(),
        measurements: chartForm.measurements,
      };
      if (selectedChartId) {
        await apiClient.put(`size-charts/${selectedChartId}`, body);
      } else {
        const created = await apiClient.post('size-charts', body);
        setSelectedChartId(created.id);
      }
      setChartForm(body);
      await loadData();
    } catch (saveError) { setError(saveError.message); }
    finally { setSavingChart(false); }
  };

  const deleteChart = async () => {
    const chart = charts.find((item) => item.id === selectedChartId);
    if (!chart || !window.confirm(`Xóa bảng size “${chart.name}”?`)) return;
    setError('');
    try {
      await apiClient.delete(`size-charts/${chart.id}`);
      setSelectedChartId('');
      setChartForm({ category_id: chartForm.category_id, name: '', measurements: emptyMeasurements(sizes) });
      await loadData();
    } catch (deleteError) { setError(deleteError.message); }
  };

  const tabs = [
    ['categories', 'Danh mục'],
    ['colors', 'Màu sắc'],
    ['sizes', 'Size'],
    ['charts', 'Bảng size'],
  ];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-lg font-bold">Danh mục, màu sắc, size &amp; bảng size</h1>
        <div className="mt-4 flex flex-wrap gap-2">
          {tabs.map(([id, label]) => (
            <button key={id} type="button" onClick={() => setTab(id)} className={`rounded-lg border px-4 py-2 text-sm font-semibold ${tab === id ? 'border-[#0f9d8a] bg-[#12383a] text-[#0f9d8a]' : 'border-[#24383b] text-[#92a9ad] hover:text-white'}`}>{label}</button>
          ))}
        </div>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>}
      {loading ? <p className="text-sm text-[#92a9ad]">Đang tải dữ liệu…</p> : (
        <>
          {tab === 'categories' && (
            <section className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
              <form onSubmit={submitCategory} className="grid gap-2 md:grid-cols-[1fr_auto]">
                <input className={inputClass} placeholder={editingCategory ? 'Tên danh mục cần sửa' : 'Tên danh mục mới'} value={categoryName} onChange={(event) => setCategoryName(event.target.value)} required />
                <button className={buttonClass} type="submit">{editingCategory ? 'Lưu thay đổi' : '+ Thêm'}</button>
              </form>
              {editingCategory && <button type="button" className="mt-2 text-xs text-[#92a9ad]" onClick={() => { setEditingCategory(null); setCategoryName(''); }}>Hủy sửa</button>}
              <div className="mt-3 divide-y divide-[#24383b]">
                {categories.map((category) => (
                  <div key={category.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                    <div><span>{category.name}</span>{!category.is_active && <span className="ml-2 text-xs text-[#92a9ad]">Đã ẩn</span>}</div>
                    <div className="flex gap-3"><button type="button" className="text-[#0f9d8a]" onClick={() => { setEditingCategory(category); setCategoryName(category.name); }}>Sửa</button><button type="button" className="text-[#92a9ad]" onClick={() => archiveCategory(category)}>Ẩn</button></div>
                  </div>
                ))}
                {categories.length === 0 && <p className="py-5 text-center text-sm text-[#92a9ad]">Chưa có danh mục.</p>}
              </div>
            </section>
          )}

          {tab === 'colors' && (
            <section className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
              <form onSubmit={submitColor} className="grid gap-2 md:grid-cols-[1fr_auto_auto]">
                <input className={inputClass} placeholder="Tên màu mới" value={colorForm.name} onChange={(event) => setColorForm({ ...colorForm, name: event.target.value })} required />
                <label className="flex items-center gap-2 rounded-lg border border-[#24383b] px-3 text-xs text-[#92a9ad]">Mã màu<input aria-label="Mã màu" type="color" className="h-8 w-10 cursor-pointer border-0 bg-transparent" value={colorForm.hex_color} onChange={(event) => setColorForm({ ...colorForm, hex_color: event.target.value })} /></label>
                <button className={buttonClass} type="submit">+ Thêm</button>
              </form>
              <div className="mt-3 divide-y divide-[#24383b]">
                {colors.map((color) => <div key={color.id} className="flex items-center justify-between py-2 text-sm"><span className="flex items-center gap-2"><span className="h-3 w-3 rounded-full border border-white/20" style={{ backgroundColor: color.hex_color }} />{color.name}<span className="text-xs text-[#92a9ad]">{color.hex_color}</span></span><button type="button" className="text-[#92a9ad] hover:text-red-400" onClick={() => deleteColor(color)}>Xóa</button></div>)}
                {colors.length === 0 && <p className="py-5 text-center text-sm text-[#92a9ad]">Chưa có màu sắc.</p>}
              </div>
            </section>
          )}

          {tab === 'sizes' && (
            <section className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
              <form onSubmit={submitSize} className="grid gap-2 md:grid-cols-[1fr_auto]">
                <input className={inputClass} placeholder="Size mới (ví dụ: XXL)" value={sizeName} onChange={(event) => setSizeName(event.target.value)} required />
                <button className={buttonClass} type="submit">+ Thêm</button>
              </form>
              <div className="mt-4 flex flex-wrap gap-2">
                {sizes.map((size) => <span key={size.id} className="inline-flex items-center gap-2 rounded-full bg-[#12383a] px-3 py-1.5 text-sm text-[#0fbdab]">{size.name}<button type="button" aria-label={`Xóa size ${size.name}`} className="text-[#92a9ad] hover:text-red-400" onClick={() => deleteSize(size)}>×</button></span>)}
                {sizes.length === 0 && <p className="py-3 text-sm text-[#92a9ad]">Chưa có size.</p>}
              </div>
            </section>
          )}

          {tab === 'charts' && (
            <form onSubmit={saveChart} className="rounded-xl border border-[#24383b] bg-[#152427] p-4">
              <div className="mb-4 grid gap-3 md:grid-cols-3">
                <label className="text-xs text-[#92a9ad]">Danh mục<select className={`${inputClass} mt-1`} value={chartForm.category_id} onChange={(event) => selectChartCategory(event.target.value)} required><option value="">Chọn danh mục</option>{categories.filter((item) => item.is_active).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
                <label className="text-xs text-[#92a9ad]">Bảng size<select className={`${inputClass} mt-1`} value={selectedChartId} onChange={(event) => selectChart(event.target.value)}><option value="">Tạo bảng mới</option>{charts.filter((chart) => chart.category_id === chartForm.category_id).map((chart) => <option key={chart.id} value={chart.id}>{chart.name}</option>)}</select></label>
                <label className="text-xs text-[#92a9ad]">Tên bảng<input className={`${inputClass} mt-1`} value={chartForm.name} onChange={(event) => setChartForm({ ...chartForm, name: event.target.value })} placeholder="Ví dụ: Bảng size áo" required /></label>
              </div>
              {sizes.length === 0 ? <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">Hãy thêm size trước khi tạo bảng size.</p> : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[700px] text-left text-sm">
                    <thead><tr className="text-xs text-[#92a9ad]"><th className="p-2">Size</th>{dimensions.map(([key, label]) => <th className="p-2" key={key}>{label}</th>)}</tr></thead>
                    <tbody>{chartForm.measurements.map((row, index) => <tr className="border-t border-[#24383b]" key={`${row.size}-${index}`}><td className="p-2 font-semibold">{row.size}</td>{dimensions.map(([key, label]) => <td className="p-2" key={key}><input aria-label={`${row.size} ${label}`} className={inputClass} value={row[key] ?? ''} onChange={(event) => updateMeasurement(index, key, event.target.value)} placeholder="Ví dụ: 150–158" /></td>)}</tr>)}</tbody>
                  </table>
                </div>
              )}
              <div className="mt-4 flex justify-end gap-2">{selectedChartId && <button type="button" className="rounded-lg border border-red-500/40 px-4 py-2 text-sm text-red-300" onClick={deleteChart}>Xóa bảng</button>}<button className={buttonClass} type="submit" disabled={savingChart || sizes.length === 0 || !chartForm.category_id}>{savingChart ? 'Đang lưu…' : 'Lưu bảng size'}</button></div>
            </form>
          )}
        </>
      )}
      <p className="text-xs text-[#92a9ad]">Màu sắc và size được lưu dùng chung, rồi chọn khi tạo biến thể trong trang Sản phẩm.</p>
    </div>
  );
};

export default Catalog;
