// Dữ liệu dùng chung cho chi tiết, yêu thích và QR. Thay bằng app-api khi có backend.
// Chưa có ảnh sản phẩm gốc: imageSource = null sẽ hiện khung chờ ảnh.
// Khi Duy có ảnh: imageSource: require('../assets/images/quan-tay.jpg').
export const demoProducts = [
  {
    id: 'SP001', name: 'Quần tây nam', category: 'Quần', season: 'Quanh năm',
    price: 900000, sold: 999, imageSource: null,
    description: 'Quần tây dáng thẳng, phù hợp đi học hoặc đi làm. Chất liệu và số lượng dưới đây là dữ liệu mẫu.',
    material: 'Vải tuyết mưa', colors: ['Đen', 'Xám'], sizes: ['S', 'M', 'L', 'XL'],
    variants: [
      { id: 'SP001-D-S', color: 'Đen', size: 'S', stock: 5 },
      { id: 'SP001-D-M', color: 'Đen', size: 'M', stock: 8 },
      { id: 'SP001-D-L', color: 'Đen', size: 'L', stock: 0 },
      { id: 'SP001-D-XL', color: 'Đen', size: 'XL', stock: 3 },
      { id: 'SP001-X-S', color: 'Xám', size: 'S', stock: 0 },
      { id: 'SP001-X-M', color: 'Xám', size: 'M', stock: 6 },
      { id: 'SP001-X-L', color: 'Xám', size: 'L', stock: 4 },
      { id: 'SP001-X-XL', color: 'Xám', size: 'XL', stock: 2 },
    ],
  },
  {
    id: 'SP002', name: 'Áo thun nam cơ bản', category: 'Áo', season: 'Mùa hè',
    price: 189000, sold: 200, imageSource: null,
    description: 'Áo thun cổ tròn, dễ phối với quần jeans hoặc quần tây. Đây là sản phẩm mẫu để kiểm tra giao diện.',
    material: 'Cotton', colors: ['Trắng', 'Đen'], sizes: ['M', 'L'],
    variants: [
      { id: 'SP002-T-M', color: 'Trắng', size: 'M', stock: 10 },
      { id: 'SP002-T-L', color: 'Trắng', size: 'L', stock: 5 },
      { id: 'SP002-D-M', color: 'Đen', size: 'M', stock: 0 },
      { id: 'SP002-D-L', color: 'Đen', size: 'L', stock: 7 },
    ],
  },
  {
    id: 'SP003', name: 'Áo khoác nhẹ', category: 'Áo', season: 'Mùa đông',
    price: 450000, sold: 85, imageSource: null,
    description: 'Áo khoác nhẹ có khóa kéo. Sản phẩm mẫu đã hết hàng để kiểm tra trạng thái không thể thêm vào giỏ.',
    material: 'Kaki', colors: ['Nâu'], sizes: ['M', 'L'],
    variants: [
      { id: 'SP003-N-M', color: 'Nâu', size: 'M', stock: 0 },
      { id: 'SP003-N-L', color: 'Nâu', size: 'L', stock: 0 },
    ],
  },
  {
    id: 'SP004', name: 'Áo sơ mi nam', category: 'Áo', season: 'Quanh năm',
    price: 299000, sold: 120, imageSource: null,
    description: 'Áo sơ mi đơn giản. Dữ liệu minh họa để xem giao diện trang chủ.',
    material: 'Cotton', colors: ['Trắng'], sizes: ['M', 'L'],
    variants: [
      { id: 'SP004-T-M', color: 'Trắng', size: 'M', stock: 5 },
      { id: 'SP004-T-L', color: 'Trắng', size: 'L', stock: 5 },
    ],
  },
];

export function getProductById(id) {
  return demoProducts.find((product) => product.id === id);
}

export function getVariant(product, color, size) {
  return product.variants.find((variant) => variant.color === color && variant.size === size);
}

export function formatPrice(value) {
  return `${value.toLocaleString('vi-VN')} ₫`;
}
