import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, FlatList, Keyboard, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import ProductCard from '../../../components/customer/ProductCard.jsx';
import { loadCategories, loadFilterOptions, searchProducts, validatePriceRange } from '../../../services/catalogApiService.js';

const empty = { min_price: '', max_price: '', color: '', size: '', in_stock_only: false, sort_by: 'newest' };
const orders = [['newest', 'Mới nhất'], ['price_asc', 'Giá tăng'], ['price_desc', 'Giá giảm']];

function Chip({ label, selected, onPress }) {
  return <Pressable onPress={onPress} style={[s.chip, selected && s.selected]} accessibilityRole="button" accessibilityState={{ selected }}>
    <Text style={[s.chipText, selected && s.selectedText]}>{label}</Text>
  </Pressable>;
}

export default function SearchScreen({ navigation }) {
  const [input, setInput] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [categoryError, setCategoryError] = useState('');
  const [metaRevision, setMetaRevision] = useState(0);
  const [options, setOptions] = useState({ colors: [], sizes: [] });
  const [optionsError, setOptionsError] = useState('');
  const [filters, setFilters] = useState(empty);
  const [draft, setDraft] = useState(empty);
  const [showFilters, setShowFilters] = useState(false);
  const [filterError, setFilterError] = useState('');
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const requestId = useRef(0);
  const mounted = useRef(true);
  const moreBusy = useRef(false);

  useEffect(() => { mounted.current = true; return () => { mounted.current = false; requestId.current += 1; }; }, []);
  useEffect(() => {
    const timer = setTimeout(() => setQuery(input.trim()), 350);
    return () => clearTimeout(timer);
  }, [input]);
  useEffect(() => {
    let active = true;
    setCategoryError('');
    loadCategories().then(rows => { if (active) setCategories(rows); })
      .catch(err => { if (active) setCategoryError(err.message); });
    return () => { active = false; };
  }, [metaRevision]);
  useEffect(() => {
    let active = true; setOptions({ colors: [], sizes: [] }); setOptionsError('');
    loadFilterOptions(category).then(value => { if (active) setOptions(value); })
      .catch(err => { if (active) setOptionsError(err.message); });
    return () => { active = false; };
  }, [category, metaRevision]);
  useEffect(() => {
    const id = ++requestId.current;
    setLoading(true); setError(''); setItems([]); setTotal(0); setPage(1); moreBusy.current = false;
    searchProducts({ ...filters, q: query, category_id: category }).then(result => {
      if (mounted.current && id === requestId.current) { setItems(result.items); setTotal(result.total); }
    }).catch(err => { if (mounted.current && id === requestId.current) setError(err.message); })
      .finally(() => { if (mounted.current && id === requestId.current) setLoading(false); });
    return () => { if (id === requestId.current) requestId.current += 1; };
  }, [query, category, filters, revision]);

  async function more() {
    if (loading || moreBusy.current || items.length >= total) return;
    moreBusy.current = true; setLoading(true); setError('');
    const id = requestId.current;
    try {
      const result = await searchProducts({ ...filters, q: query, category_id: category }, page + 1);
      if (!mounted.current || id !== requestId.current) return;
      setItems(current => [...new Map([...current, ...result.items].map(p => [p.id, p])).values()]);
      setTotal(result.total); setPage(page + 1);
    } catch (err) { if (mounted.current && id === requestId.current) setError(err.message); }
    finally { if (mounted.current && id === requestId.current) { setLoading(false); moreBusy.current = false; } }
  }
  function selectCategory(id) {
    setCategory(id); setFilters(current => ({ ...current, color: '', size: '' }));
    setDraft(current => ({ ...current, color: '', size: '' }));
  }
  function applyFilters() {
    const message = validatePriceRange(draft.min_price, draft.max_price);
    setFilterError(message);
    if (message) return;
    Keyboard.dismiss(); setFilters({ ...draft }); setShowFilters(false);
  }
  function reset() {
    setInput(''); setQuery(''); setCategory(''); setFilters({ ...empty }); setDraft({ ...empty }); setFilterError('');
  }

  return <SafeAreaView style={s.page} edges={['top', 'bottom']}>
    <View style={s.header}>
      <Pressable onPress={() => navigation.goBack()} style={s.icon} accessibilityRole="button" accessibilityLabel="Quay lại"><Ionicons name="chevron-back" size={25} /></Pressable>
      <Text style={s.title}>Danh mục & tìm kiếm</Text>
      <Pressable style={s.icon} accessibilityRole="button" accessibilityLabel="Bộ lọc" onPress={() => { setDraft({ ...filters }); setFilterError(''); setShowFilters(!showFilters); }}><Ionicons name="options-outline" size={25} /></Pressable>
    </View>
    <View style={s.search}>
      <Ionicons name="search-outline" size={22} />
      <TextInput style={s.searchInput} placeholder="Tên, mã hoặc mô tả sản phẩm" value={input} onChangeText={setInput} maxLength={100} returnKeyType="search" onSubmitEditing={() => { setQuery(input.trim()); Keyboard.dismiss(); }} accessibilityLabel="Tìm kiếm sản phẩm" />
      {!!input && <Pressable style={s.icon} onPress={() => { setInput(''); setQuery(''); }} accessibilityLabel="Xóa từ khóa" accessibilityRole="button"><Ionicons name="close" size={20} /></Pressable>}
    </View>
    <View><ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.chips}>
      <Chip label="Tất cả" selected={!category} onPress={() => selectCategory('')} />
      {categories.map(c => <Chip key={c.id} label={c.name} selected={category === c.id} onPress={() => selectCategory(c.id)} />)}
    </ScrollView></View>
    {!!categoryError && <Pressable onPress={() => setMetaRevision(v => v + 1)}><Text style={s.error}>Không tải được danh mục. Chạm để thử lại.</Text></Pressable>}
    {showFilters && <ScrollView style={s.filterPanel} keyboardShouldPersistTaps="handled">
      <Text style={s.label}>Khoảng giá (VNĐ)</Text>
      <View style={s.row}>{[['min_price', 'Từ'], ['max_price', 'Đến']].map(([key, label]) => <TextInput key={key} style={s.priceInput} value={draft[key]} placeholder={label} keyboardType="number-pad" maxLength={12} onChangeText={value => setDraft(v => ({ ...v, [key]: value }))} accessibilityLabel={`Giá ${label}`} />)}</View>
      <Text style={s.label}>Màu</Text><View style={s.wrap}><Chip label="Tất cả" selected={!draft.color} onPress={() => setDraft(v => ({ ...v, color: '' }))} />{options.colors.map(color => <Chip key={color} label={color} selected={draft.color === color} onPress={() => setDraft(v => ({ ...v, color }))} />)}</View>
      <Text style={s.label}>Kích thước</Text><View style={s.wrap}><Chip label="Tất cả" selected={!draft.size} onPress={() => setDraft(v => ({ ...v, size: '' }))} />{options.sizes.map(size => <Chip key={size} label={size} selected={draft.size === size} onPress={() => setDraft(v => ({ ...v, size }))} />)}</View>
      {!!optionsError && <Pressable onPress={() => setMetaRevision(v => v + 1)}><Text style={s.error}>Không tải được màu/size. Chạm để thử lại.</Text></Pressable>}
      <View style={s.between}><Text>Chỉ sản phẩm còn hàng</Text><Switch value={draft.in_stock_only} onValueChange={value => setDraft(v => ({ ...v, in_stock_only: value }))} /></View>
      <Text style={s.label}>Sắp xếp</Text><View style={s.wrap}>{orders.map(([key, label]) => <Chip key={key} label={label} selected={draft.sort_by === key} onPress={() => setDraft(v => ({ ...v, sort_by: key }))} />)}</View>
      {!!filterError && <Text style={s.error}>{filterError}</Text>}
      <Pressable style={s.apply} onPress={applyFilters} accessibilityRole="button"><Text style={s.selectedText}>Áp dụng bộ lọc</Text></Pressable>
    </ScrollView>}
    <View style={s.summary}><Text style={s.muted}>{loading && !items.length ? 'Đang tìm…' : `${total} sản phẩm`}</Text><Pressable onPress={reset}><Text style={s.link}>Xóa bộ lọc</Text></Pressable></View>
    <FlatList data={items} numColumns={2} keyExtractor={item => item.id} columnWrapperStyle={s.grid} contentContainerStyle={s.list} keyboardShouldPersistTaps="handled"
      refreshing={loading && !items.length} onRefresh={() => setRevision(v => v + 1)}
      renderItem={({ item }) => <ProductCard product={item} onOpen={() => navigation.navigate('ProductDetail', { productId: item.id })} />}
      ListEmptyComponent={!loading ? <View style={s.empty}><Ionicons name="search-outline" size={38} color="#888" /><Text style={s.muted}>{error || 'Không có sản phẩm phù hợp. Thử từ khóa hoặc bộ lọc khác.'}</Text>{!!error && <Pressable onPress={() => setRevision(v => v + 1)}><Text style={s.link}>Thử lại</Text></Pressable>}</View> : null}
      ListFooterComponent={<View style={s.footer}>{!!error && items.length > 0 && <Text style={s.error}>{error}</Text>}{loading ? <ActivityIndicator color="#111" /> : items.length > 0 && items.length < total ? <Pressable style={s.more} onPress={more}><Text>Tải thêm sản phẩm</Text></Pressable> : null}</View>} />
  </SafeAreaView>;
}

const s = StyleSheet.create({
  page: { flex: 1, backgroundColor: '#fff' }, header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, minHeight: 56 },
  icon: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' }, title: { flex: 1, textAlign: 'center', fontSize: 18, fontWeight: '600' },
  search: { marginHorizontal: 16, borderWidth: 1, borderColor: '#ccc', borderRadius: 8, flexDirection: 'row', alignItems: 'center', paddingLeft: 12 }, searchInput: { flex: 1, minHeight: 46, paddingHorizontal: 10, color: '#111' },
  chips: { paddingHorizontal: 16, paddingVertical: 12, gap: 8 }, chip: { minHeight: 40, paddingHorizontal: 14, borderWidth: 1, borderColor: '#ddd', borderRadius: 6, justifyContent: 'center' }, selected: { backgroundColor: '#111', borderColor: '#111' }, chipText: { color: '#333' }, selectedText: { color: '#fff', fontWeight: '600' },
  filterPanel: { maxHeight: 330, flexGrow: 0, marginHorizontal: 16, paddingHorizontal: 12, backgroundColor: '#f7f7f7', borderRadius: 8 }, label: { fontWeight: '600', marginTop: 14, marginBottom: 8 }, row: { flexDirection: 'row', gap: 10 }, priceInput: { flex: 1, minHeight: 44, borderWidth: 1, borderColor: '#ddd', borderRadius: 6, paddingHorizontal: 10, backgroundColor: '#fff' }, wrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 }, between: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 10 },
  apply: { minHeight: 44, backgroundColor: '#111', alignItems: 'center', justifyContent: 'center', borderRadius: 6, marginVertical: 16 }, summary: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 10 }, muted: { color: '#666', lineHeight: 21 }, link: { color: '#222', textDecorationLine: 'underline', paddingVertical: 4 },
  list: { paddingHorizontal: 16, paddingBottom: 24, flexGrow: 1 }, grid: { justifyContent: 'space-between' }, error: { color: '#b42318', paddingHorizontal: 16, paddingVertical: 8 }, empty: { alignItems: 'center', paddingVertical: 36, gap: 14 }, footer: { alignItems: 'center', padding: 10 }, more: { borderWidth: 1, borderColor: '#bbb', borderRadius: 6, padding: 12 },
});
