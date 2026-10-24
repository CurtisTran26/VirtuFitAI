# VirtuFitAI — tích hợp có đối chiếu nguồn, 22/10/2026

## Nền và phạm vi

Nền chính xác: ZIP Duy gửi `VirtuFitAI-review-20261021-152319.zip` (backend, database, frontend/mobile/src). Đây đã là bản Giáp + gói mobile 20/10, không phải code nguyên bản Giáp.
Nhánh tham chiếu: Giáp `backend/giap-sprint-1` tại `8c800d2265322bfd33a407b5f4d349ec934db7f7`; An `backend/an-sprint1` tại `8079668`.
Gói này là patch có chuyển đổi tương thích, KHÔNG phải merge nguyên hai nhánh, không ghi rằng mọi module của An đang chạy.
Không push GitHub hoặc đổi main. Management API cập nhật cấu trúc module mới của Giáp; shared sessions, migration và tài khoản hiện có được giữ.

## Quyết định của Duy

Duy nhận luôn S1-020 — Danh mục và tìm kiếm Customer/PB13 trên mobile. Lộc làm frontend web quản lý.
Không tạo mã PB mới. Tài liệu này ghi nhận thay đổi; file Excel/Google Sheets của nhóm chưa được tự sửa.

## Nguồn gốc phần thực thi

| Thành phần | Nguồn | Cách nối |
|---|---|---|
| users, products, roles, biến thể, sessions UUID; Management API | Nền Giáp và bản Duy gửi | Management API lấy bản module mới của Giáp; dữ liệu giữ nguyên |
| Đăng ký/password/wishlist | Nền Giáp, đã sửa trong gói 20/10 | Giữ hợp đồng API và cơ chế xác thực |
| SMS strategy/Twilio | An `integrations/phone_otp/provider.py` | Chuyển async sang sync cho endpoint hiện tại; loại silent mock fallback; hỗ trợ tên biến cũ và của An |
| Google | Bộ xác minh chữ ký google-auth của bản 20/10 | Giữ bộ xác minh thật; hỗ trợ GOOGLE_CLIENT_ID của An; chặn cấu hình mâu thuẫn và token mock. KHÔNG copy tokeninfo/mock verifier của An |
| OTP storage | PostgreSQL của bản UUID | Không chạy Redis/JWT OTP của An song song |
| Bộ lọc catalog | Hành vi `services/catalog/service.py` của An | Viết lại truy vấn trên products/product_variants của Giáp; giữ response mobile; đếm đúng query đã lọc |
| QR PNG | Thuật toán QRCode của An `services/qr_scan/service.py` | Dùng lại sinh PNG; chuyển resolver sang UUID/SKU; thêm GET alias và endpoint PNG có quyền |
| Private avatar storage | Thiết kế upload/object-key/presign của An S3StorageService | Chuyển sang UUID; ký URL bằng endpoint public ngay từ đầu, không thay host sau ký |
| Hồ sơ | Endpoint UUID đã có | Khi bật storage S3: lưu object reference, trả URL có hạn khi đọc hồ sơ; mặc định giữ data URI để cấu hình hiện tại chạy |
| SearchScreen và catalogApiService | Mới, bổ sung cho phần Duy nhận | Dùng API thật, không danh mục/sản phẩm mock; giữ ProductCard, chi tiết và wishlist sẵn có |

Các file `app/team_integrations/*` là bản chuyển đổi tương thích (có sửa/viết mới), không gán toàn bộ mã mới là code nguyên bản An. Có thể đối chiếu nguồn tại GitHub theo commit trên.

## Không ghép được nguyên trạng vì

- Giáp: `users.id` UUID, `role_id`, phiên token opaque trong PostgreSQL. An: `user_id` integer, role enum, JWT.
- Giáp: `products.id`, `price_vnd`, `product_variants(size,color,stock_on_hand)`. An: `product_id`, `price`, product_sizes, product_images, store.
- ID số nguyên/QR cũ từ database An không tự ánh xạ tới UUID. Phải tạo lại QR hoặc thiết kế migration dữ liệu riêng nếu cần nhập dữ liệu An.
- Đường dẫn trùng không làm hai cơ chế xác thực tự tương thích. Không chạy migration Alembic của An vào database UUID.

## Hợp đồng API mobile giữ ổn định

- POST `/api/v1/auth/otp`, `/auth/register`, `/auth/login`, `/auth/google`, `/auth/logout`, `/auth/verify-reset-otp`, `/auth/reset-password`, `/auth/change-password`.
- GET/PUT `/api/v1/users/me`; PUT nhận `avatar_data` data URI, ảnh được kiểm tra và re-encode.
- GET `/api/v1/catalog/categories`, `/catalog/products`, `/catalog/products/{UUID}`.
- GET/PUT/DELETE wishlist như gói hiện tại.
- POST `/api/v1/qr/scan` nhận `{content}`, trả `{product}`; GET cùng path nhận `code` là alias, vẫn trả `{product}`.
- Mới: GET `/api/v1/catalog/filter-options?category_id=UUID` trả colors/sizes.
- Mới: GET `/api/v1/qr/products/{UUID}/image` trả PNG, chỉ admin/warehouse_staff/sales_staff.

Catalog hỗ trợ q/category_id/min_price/max_price/color/size/in_stock_only/sort_by/page/limit (page_size là alias).
Giá là số nguyên VNĐ. sort_by: newest, price_asc, price_desc. Màu/size so khớp không phân biệt hoa thường và cùng một biến thể. Bộ lọc chỉ còn hàng kiểm tra chính biến thể đó.
Chưa chuyển store/category phân cấp/popular/try-on count của An vì schema Giáp chưa có dữ liệu tương ứng; không giả trả chức năng đó.

## Bản mới của Giáp và cách ghép ngày 22/10

Đã đọc trực tiếp nhánh Giáp tại 8c800d2 và An tại 8079668 ngày 22/10/2026.
Giáp tách main.py thành schemas/auth.py, services/auth.py, routers/auth/router.py, routers/wishlist/router.py.
Management API mới có routers auth/roles/users/categories/products/inventory; các thư mục trống khác không phải chức năng đã hoàn thành.
Bản tích hợp dùng cấu trúc này nhưng bổ sung hợp đồng mobile đang chạy: Google, reset-token, OTP đổi mật khẩu, profile, catalog, QR và wishlist chi tiết.
Các logic tương thích mobile trong auth/services đã có sửa/viết mới, không gọi là code nguyên bản Giáp.

File chính để nhóm cùng sửa tiếp:
- backend/app-api/app/main.py: khởi tạo, error handlers, health, include_router.
- backend/app-api/app/config.py: đọc .env.integration đúng thư mục.
- backend/app-api/app/routers/auth/router.py và services/auth.py: auth + OTP + reset ticket.
- backend/app-api/app/routers/wishlist/router.py: wishlist kèm variants và lọc active.
- backend/app-api/app/routers/profiles/router.py, services/profiles.py: hồ sơ.
- backend/app-api/app/routers/catalog/router.py, services/catalog.py: API sản phẩm.
- backend/app-api/app/routers/qr/router.py: quét và sinh QR.
- backend/app-api/app/team_integrations/: các phần chuyển đổi từ thiết kế/code của An.

Không chạy đồng thời auth JWT/Redis của An với session PostgreSQL của Giáp. Không áp dụng schema integer/Alembic của An vào database UUID hiện tại.
Không ghép API media upload/presign công khai của An: cần kiểm tra quyền và sở hữu ảnh trước khi mở rộng; bản này chỉ nối avatar qua tài khoản đăng nhập.
Không mang gợi ý size theo BMI, store/popular/try-on-count hoặc PoC AI vào Sprint 1 mobile trong gói này.

## Giới hạn rõ ràng

- Không đưa toàn bộ An ORM/JWT/Redis vào chạy; tích hợp theo contract UUID có chuyển đổi như bảng trên.
- Không ghép frontend web của Lộc, không làm AI/checkout/sprint sau.
- SMS thật cần tài khoản nhà cung cấp và thử gửi; chỉ HTTP thành công không chứng minh thiết bị đã nhận SMS.
- Cloud storage tùy chọn cần hạ tầng và bucket riêng; không tự triển khai MinIO hoặc tạo quyền public.
- QR PNG là API backend; UI web quản lý tải QR thuộc Lộc, chưa được viết trong gói này.
- Gói không tự tạo sản phẩm. Nếu database rỗng, màn danh mục/tìm kiếm sẽ hiển thị rỗng đúng dữ liệu.
