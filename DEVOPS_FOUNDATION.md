# HƯỚNG DẪN HẠ TẦNG & NHẬT KÝ THAY ĐỔI (DEVOPS & BACKEND FOUNDATION)

> **Dự án:** VirtuFit AI — Hệ thống thương mại điện tử thời trang tùy chỉnh tích hợp AI  
> **Người thực hiện:** Đội ngũ Backend & DevOps  
> **Cập nhật lần cuối:** 30/10/2026  
> **Tài liệu này được duy trì và cập nhật liên tục sau mỗi tính năng hoàn thành.**

---

## 📌 Bảng phân công & Phạm vi ảnh hưởng

| Thành viên | Vai trò phụ trách | Hướng dẫn kết nối & lưu ý |
| :--- | :--- | :--- |
| **Giáp** | Backend / App API | Phát triển nghiệp vụ chính trên `backend/app-api`, kế thừa router health check và cấu hình config. |
| **An** | Backend / Management API | Có thể nhân bản cấu hình Dockerfile và router health check sang `backend/management-api` (chạy port 8001). |
| **Duy** | Frontend / Mobile (Expo) | Kết nối API qua base URL: Máy ảo Android (`http://10.0.2.2:8000`), Máy thật (`http://<IP-LAN>:8000`). |
| **Lộc** | Frontend / Web (React + Vite) | Kết nối API qua `http://localhost:8000`. CORS đã được mở sẵn cho port `5173` và `3000`. |
| **Trinh** | Docs & Testing | Kiểm tra tính sẵn sàng của hệ thống qua endpoint `/health/ready` trước khi chạy test case. |

---

## 🚀 Nhật ký các hạng mục đã triển khai (Changelog)

### [Giai đoạn 1] Thiết lập Hạ tầng cơ sở (Foundation Setup) — *Hoàn thành*

#### 1. Quản lý mã nguồn & Git Configuration
- [x] **Cập nhật `.gitignore` toàn diện:** Loại trừ tuyệt đối các file nhạy cảm (`.env*`, chứng chỉ `*.pem`, `*.key`), cache Python (`__pycache__`, `.venv`, `.pytest_cache`), rác Node.js/Expo (`node_modules`, build APK/AAB), volumes dữ liệu và file hệ điều hành/IDE.
- [x] **Chuẩn hóa Git Workflow:** Thống nhất áp dụng **GitHub Flow** (nhánh chính `main` luôn deployable; tính năng mới tách nhánh `feat/<tên-tính-năng>`, sửa lỗi tách nhánh `fix/<tên-lỗi>`).
- [x] **Quy chuẩn Conventional Commits:** Định dạng `<type>(<scope>): <summary>` (ví dụ: `feat(auth): add phone otp verification`, `fix(db): resolve pool leak`).

#### 2. Quản lý biến môi trường an toàn
- [x] **Tạo `.env.example` chuẩn công nghiệp:** Phân nhóm trực quan theo 6 module:
  - `APP_*`: Cấu hình máy chủ FastAPI (Host, Port, Debug, Version).
  - `DB_*` / `DATABASE_URL`: Cấu hình PostgreSQL 16 và connection pool.
  - `REDIS_*` / `REDIS_URL`: Cấu hình Redis 7 (cache, session, TTL).
  - `JWT_*`: Khóa bí mật ký token, thuật toán HS256, thời hạn access/refresh token.
  - `CORS_*`: Cấp phép origins gọi API cho Web (Vite) và Mobile.
  - `STORAGE_*`: Thông số kết nối Object Storage (MinIO/S3) lưu ảnh thử đồ.

#### 3. Container hóa môi trường phát triển (Docker & Docker Compose)
- [x] **Tạo `docker-compose.yml` tối ưu:**
  - **Service `postgres` (PostgreSQL 16 Alpine):** Có Named Volume `postgres_data` chống mất dữ liệu khi restart; tích hợp healthcheck `pg_isready`.
  - **Service `redis` (Redis 7 Alpine):** Có Named Volume `redis_data` lưu snapshot AOF; tích hợp healthcheck `redis-cli ping`.
  - **Service `app-api` (FastAPI):** Mount volume mã nguồn để **Hot-Reloading** tự động khi code; áp dụng `depends_on: condition: service_healthy` để loại bỏ triệt để lỗi "API khởi động trước khi Database sẵn sàng".
  - **Mạng nội bộ cô lập (`virtufit_network`):** Các service kết nối an toàn qua DNS nội bộ (`postgres:5432`, `redis:6379`).
  - **Chính sách tự phục hồi:** `restart: unless-stopped`.
- [x] **Xây dựng Dockerfile cho Backend:** Sử dụng base image nhẹ `python:3.11-slim`, tối ưu layer cache pip, tự động reload Uvicorn.

#### 4. Hệ thống kiểm tra sức khỏe dịch vụ (Cloud-Native Health Checks)
- [x] **Tạo Router `/health` tại `backend/app-api/app/routers/health.py`:**
  - `GET /health/live` (Liveness Probe): Kiểm tra nội tại tiến trình FastAPI có bị đơ/deadlock hay không.
  - `GET /health/ready` (Readiness Probe): Ping thực tế đến PostgreSQL và Redis. Nếu 1 trong 2 dịch vụ ngắt kết nối, tự động trả về `503 Service Unavailable`.
  - `GET /health` (General Info): Trả về phiên bản và thông tin vận hành hệ thống.
- [x] **Khởi tạo Entrypoint FastAPI:** `backend/app-api/app/main.py` tích hợp sẵn CORS Middleware và Swagger UI tại `/docs`.

### [Giai đoạn 2] Cloud Object Storage & Phân quyền hình ảnh (MinIO / S3) — *Hoàn thành*

#### 1. Hạ tầng Object Storage (MinIO)
- [x] **Tích hợp MinIO vào Docker Compose:** Chạy song song S3 API (cổng `9000`) và Web Console Dashboard (cổng `9001`).
- [x] **Tự động khởi tạo Buckets (Auto-Provisioning):** Sử dụng container phụ trợ `createbuckets` (`minio/mc`) tự động tạo 2 bucket:
  - `virtufit-public`: Quyền tải công khai (`download` policy) dành cho ảnh sản phẩm, banner, QR code.
  - `virtufit-private`: Quyền riêng tư (`none` policy) dành cho ảnh người dùng thử đồ, kết quả AI try-on, thiết kế custom.
- [x] **Dữ liệu bền vững (Persistence):** Named Volume `minio_data` đảm bảo không bị mất ảnh khi khởi động lại container.

#### 2. Phân quyền và Bảo mật hình ảnh (Image Security & Permissions)
- [x] **Kiểm tra an toàn file tải lên (`validator.py`):**
  - Giới hạn đuôi file: `.jpg`, `.jpeg`, `.png`, `.webp`.
  - Giới hạn dung lượng: Tối đa 5MB.
  - Kiểm tra Magic Bytes thực tế ở header file (chống hacker đổi đuôi file mã độc `.exe`/`.php` thành `.jpg`).
- [x] **Dịch vụ S3 Storage (`service.py`):**
  - Tự động sinh tên file định danh duy nhất (UUID v4) chống trùng lặp.
  - Phân luồng lưu trữ theo tham số `is_public`:
    - Public: Trả về URL trực tiếp không hết hạn.
    - Private: Sinh **Presigned URL** có thời hạn sống (mặc định 30 phút / 1800s).
- [x] **API Endpoints (`app/routers/media.py`):**
  - `POST /media/upload`: Nhận file multipart/form-data, validate, đẩy lên MinIO và trả metadata kèm URL.
  - `GET /media/presigned-url`: Sinh URL tạm thời mới để xem/tải ảnh riêng tư theo `object_key`.
- [x] **Tích hợp Readiness Probe:** `/health/ready` tự động ping kiểm tra kết nối tới MinIO song song cùng PostgreSQL & Redis.

### [Giai đoạn 3] API Catalog, Tìm kiếm, Bộ lọc & Chi tiết sản phẩm — *Hoàn thành*

#### 1. Mô hình dữ liệu chung (Shared SQLAlchemy Models)
- [x] **`Store` (`backend/shared/models/store.py`):** Cửa hàng thời trang, địa chỉ, số điện thoại, trạng thái hoạt động.
- [x] **`Category` (`backend/shared/models/category.py`):** Cây danh mục thời trang đa cấp (Self-referencing tree: Áo nam -> Áo thun nam, Áo sơ mi nam,...).
- [x] **`Product`, `ProductImage`, `ProductSize` (`backend/shared/models/product.py`):** 
  - Lưu thông tin sản phẩm, giá bán, giá khuyến mãi (`discount_price`), màu sắc, số lượt xem (`view_count`), số lượt thử đồ (`try_on_count`).
  - Hỗ trợ bộ sưu tập nhiều ảnh (`sort_order`, `is_primary`).
  - Quản lý kích thước may mặc chi tiết: size S/M/L/XL, tồn kho `stock_quantity`, số đo ngực (`chest_cm`), eo (`waist_cm`), dài (`length_cm`) phục vụ tính năng AI Virtual Try-On và gợi ý size.

#### 2. Tầng nghiệp vụ & Kiến trúc mở rộng (Service Layer)
- [x] **Truy vấn tối ưu trực tiếp DB:** Dùng dynamic queries SQLAlchemy với `selectinload` để loại trừ triệt để lỗi N+1 Query.
- [x] **Thiết kế sẵn đường lui cho Redis Caching:** Tách biệt `CatalogService` thành lớp độc lập. Khi cần tối ưu tải cao, chỉ cần bổ sung decorator/cache middleware bọc ngoài mà không cần sửa router hay schemas.

#### 3. Bộ API Catalog chuẩn RESTful (`/catalog/*`)
- [x] **`GET /catalog/categories`:** Lấy toàn bộ cây danh mục phân cấp cha - con.
- [x] **`GET /catalog/products`:** Tìm kiếm và lọc sản phẩm đa tiêu chí:
  - `q`: Tìm kiếm gần đúng (case-insensitive) theo tên hoặc mô tả.
  - `category_id`: Lọc theo danh mục (tự động bao gồm cả danh mục con).
  - `min_price`, `max_price`: Lọc theo khoảng giá ngân sách.
  - `color`: Lọc theo màu sắc (Trắng, Đen, Be, Xanh,...).
  - `size`: Lọc theo size thực tế còn hàng trong kho (S, M, L, XL).
  - `in_stock_only`: Chỉ hiển thị sản phẩm còn hàng (`stock_quantity > 0`).
  - `sort_by`: Sắp xếp linh hoạt (`newest`, `price_asc`, `price_desc`, `popular`, `try_on`).
  - `page`, `page_size`: Phân trang chuẩn với đầy đủ `total`, `total_pages`.
- [x] **`GET /catalog/products/{product_id}`:** Chi tiết sản phẩm, toàn bộ thư viện ảnh, bảng thông số đo áo, tự động tăng `view_count`.

#### 4. Kịch bản nạp dữ liệu mẫu thực tế & Idempotent (`seed.py`)
- [x] **Tách biệt & Idempotent (`backend/shared/database/seed.py`):** Chạy lại bao nhiêu lần cũng không nhân bản (duplicate) dữ liệu.
- [x] **Dữ liệu thực tế:** 1 Cửa hàng Flagship, 13 danh mục phân cấp, 10 sản phẩm thời trang Việt Nam (VNĐ, size Việt, số đo cm thực tế).
- [x] **Đầy đủ kịch bản kiểm thử (Positive & Negative Test Cases):**
  - *Positive:* Hàng bán chạy, giảm giá sốc, đủ size còn hàng, nhiều ảnh.
  - *Negative 1 (Hết hàng):* `Áo Khoác Bomber Limited Edition` có tồn kho = 0 ở mọi size (để test bộ lọc `in_stock_only=true`).
  - *Negative 2 (Sản phẩm ẩn):* `Áo Thun Mẫu Cũ Ngừng Kinh Doanh` có `is_active=False` (kiểm tra không bao giờ rò rỉ ra catalog).
  - *Negative 3 (Lẻ size):* `Quần Tây Âu Classic` chỉ còn đúng 1 chiếc size XL (để test lọc `size=M` thì không ra, `size=XL` thì ra).
- [x] **Kích hoạt bằng 1 lệnh duy nhất:** Dễ dàng chạy từ máy host hoặc trực tiếp trong container.

### [Giai đoạn 4] Quét mã QR tại cửa hàng & Resolve thông tin sản phẩm (In-Store QR Code Scan) — *Hoàn thành*

#### 1. Nguyên lý nghiệp vụ & Quy tắc hệ thống (Business Rules)
- [x] **Trải nghiệm O2O (Online-to-Offline):** Khách hàng đến cửa hàng vật lý, dùng ứng dụng Mobile (hoặc camera điện thoại) quét mã QR đính trên tem mác áo/quần để mở ngay trang chi tiết sản phẩm và kích hoạt **Phòng thử đồ ảo AI (AI Try-On Fitting Room)** với số đo cơ thể cá nhân.
- [x] **Quy tắc phân biệt QR (README):** `QR sản phẩm KHÁC QR chuyển khoản thanh toán`. QR sản phẩm dùng để tra cứu thông tin sản phẩm và thử đồ; QR chuyển khoản là mã VietQR/VNPay phục vụ thanh toán đơn hàng.

#### 2. Dịch vụ phân giải đa định dạng (`backend/app-api/app/services/qr_scan/service.py`)
- [x] **Nhận diện linh hoạt đa định dạng QR:**
  - *Deep Link di động:* `virtufit://product/{id}` (mở thẳng trong ứng dụng React Native của bạn Duy).
  - *Web URL chuẩn:* `https://virtufit.vn/products/{id}` (quét bằng camera iPhone/Android thông thường cũng mở được).
  - *Mã định danh mã vạch:* `VF-PROD-0001` hoặc ID thuần túy `1`.
  - *Tra cứu DB:* Tự động query bảng `product_qr_codes` nếu quét mã chuỗi ngẫu nhiên.
- [x] **Kiểm tra an toàn & Trạng thái kinh doanh:** Chỉ resolve các sản phẩm có `is_active == True`. Nếu sản phẩm đã ngừng kinh doanh hoặc không tồn tại, trả về lỗi rõ nghĩa `HTTP 404`.
- [x] **Đánh giá tính sẵn sàng cho AI Try-On (`try_on_ready`):** Tự động kiểm tra sản phẩm có đủ hình ảnh và thông số may mặc (ngực, eo, dài) hay không để bật tính năng thử đồ.
- [x] **Tự động tăng `view_count`:** Đếm lượt quan tâm thực tế của khách hàng tại cửa hàng vật lý.

#### 3. API Endpoint chuẩn OpenAPI Contract (`GET /api/v1/qr/scan`)
- [x] **`GET /api/v1/qr/scan?code=...`:** Nhận chuỗi quét được, giải mã và trả về toàn bộ thông tin sản phẩm, bảng size, thông số số đo, ảnh sản phẩm, liên kết Deep Link và Web URL.

#### 4. Khả năng sinh ảnh QR chuẩn chất lượng cao
- [x] **Thư viện chuẩn `qrcode[pil]`:** Cung cấp sẵn hàm sinh ảnh QR PNG chất lượng cao, upload tự động lên MinIO public bucket `virtufit-public/qr-codes/` để in tem mác vật lý (sẵn sàng cho Management API sau này).

### [Giai đoạn 5] API Hồ sơ người dùng & Số đo may mặc cho AI Try-On (Profile & Measurements) — *Hoàn thành*

#### 1. Cơ chế Xác thực Linh hoạt & Tiện lợi (Security & Auth Dependencies)
- [x] **JWT Bearer Token chuẩn RFC 6750 (`security.py`):** Xác thực chữ ký token, hạn sử dụng và giải mã `user_id`.
- [x] **Cơ chế Dev Mode Fallback:** Để hỗ trợ đội Frontend (Duy - Mobile, Lộc - Web) kiểm thử ngay lập tức mà không bị nghẽn ở màn hình đăng nhập:
  - Chấp nhận Bearer token dạng `dev-token-<user_id>`.
  - Chấp nhận custom header `X-User-Id: <user_id>`.
  - Tự động fallback lấy Customer mẫu đầu tiên trong DB khi dev nếu không truyền header nào.

#### 2. Dịch vụ Hồ sơ cá nhân (`backend/app-api/app/services/profile/service.py`)
- [x] **Tích hợp thông số thử đồ AI:** Tự động tính chỉ số khối cơ thể **BMI** và **đề xuất size quần áo chuẩn theo form người Việt** (S, M, L, XL, XXL) dựa trên chiều cao (`height_cm`) và cân nặng (`weight_kg`).
- [x] **Đổi mật khẩu an toàn:** Mã hóa bằng thuật toán `bcrypt`, bắt buộc xác thực mật khẩu cũ và ngăn chặn đặt mật khẩu mới trùng mật khẩu cũ.
- [x] **Tải ảnh đại diện trực tiếp (Direct Avatar Upload):** Kiểm tra an toàn file ảnh, tự động đẩy lên MinIO public bucket `virtufit-public/avatars/` và lưu URL mới vào hồ sơ.

#### 3. Bộ API Profile đầy đủ (`/api/v1/users/me*`)
- [x] **`GET /api/v1/users/me`:** Lấy thông tin cá nhân, vai trò, số đo chiều cao, cân nặng, BMI và size đề xuất.
- [x] **`PUT /api/v1/users/me`:** Cập nhật họ tên, giới tính, chiều cao (cm), cân nặng (kg) và ảnh đại diện.
- [x] **`PUT /api/v1/users/me/password`:** Đổi mật khẩu tài khoản.
- [x] **`POST /api/v1/users/me/avatar`:** Upload trực tiếp file ảnh avatar lên MinIO.

### [Giai đoạn 6] Tích hợp Xác thực OTP Điện thoại & Đăng nhập không cần mật khẩu (Phone OTP & Passwordless Login) — *Hoàn thành*

#### 1. Kiến trúc Provider gửi SMS linh hoạt (Strategy Pattern)
- [x] **`MockSMSProvider` (Mặc định cho Dev & Đồ án):** In mã OTP nổi bật ra màn hình Terminal console kèm thông tin thời gian; trả về `debug_otp` trong response khi `APP_DEBUG=true` để đội Mobile (bạn Duy) và Web (bạn Lộc) test liền mạch mà không tốn chi phí SMS.
- [x] **`TwilioSMSProvider`:** Hỗ trợ cắm API credentials qua biến môi trường (`SMS_PROVIDER=twilio`) để gửi SMS thật đến mọi nhà mạng Việt Nam.

#### 2. Quản lý mã OTP và Bảo mật chống Brute-force với Redis
- [x] **Tự động hết hạn (TTL):** Lưu mã OTP 6 chữ số ngẫu nhiên trong Redis với thời hạn sống 5 phút (`OTP_TTL_SECONDS=300`).
- [x] **Chống Spam SMS (Cooldown 60s):** Cơ chế khóa tạm thời 60 giây giữa 2 lần bấm "Gửi lại mã" (`otp:cooldown:{phone}`).
- [x] **Chống Brute-force (Tối đa 3 lần thử):** Nếu người dùng nhập sai mã quá 3 lần, hệ thống lập tức hủy mã OTP trong Redis để chống hacker dò mã tự động.
- [x] **Verification Token:** Khi verify thành công, sinh `verification_token` dùng một lần (TTL 10 phút) để đảm bảo tính toàn vẹn cho các bước đăng ký/đổi mật khẩu.

#### 3. Bộ API Xác thực qua Điện thoại đầy đủ (`/api/v1/auth/*`)
- [x] **`POST /api/v1/auth/otp/send`:** Chuẩn hóa số điện thoại Việt Nam (+84 / 090...), tạo mã 6 số, gửi SMS và trả thời gian cooldown.
- [x] **`POST /api/v1/auth/otp/verify`:** Xác thực mã OTP và cấp `verification_token`.
- [x] **`POST /api/v1/auth/otp/login` (Passwordless Login):** Khách hàng chỉ cần nhập SĐT + OTP để đăng nhập. Nếu là số điện thoại mới, hệ thống **tự động tạo tài khoản Customer** và cấp cặp JWT Access Token (hạn 7 ngày) + Refresh Token (hạn 30 ngày).
- [x] **`POST /api/v1/auth/password/reset-with-otp`:** Quên mật khẩu có thể xác thực bằng OTP và đặt lại mật khẩu mới mà không cần email OTP (đúng theo quy tắc nghiệp vụ `README.md`).

### [Giai đoạn 7] Xác minh Google OAuth2 ID Token & Đăng nhập một chạm (Google Token Verification) — *Hoàn thành*

#### 1. Cơ chế Xác minh kép (Dual Verification Architecture)
- [x] **Xác minh trực tiếp với Google OAuth2 API (`verifier.py`):** Sử dụng endpoint chuẩn `https://oauth2.googleapis.com/tokeninfo?id_token=...` bằng `httpx` bất đồng bộ để kiểm tra chữ ký mã hóa, thời hạn sống của token, trạng thái `email_verified`, và đối chiếu Audience `aud == GOOGLE_CLIENT_ID`.
- [x] **Hỗ trợ Mock Token khi Development:** Để đội Mobile (**Duy**) và Web (**Lộc**) có thể phát triển và kiểm thử giao diện đăng nhập Google ngay lập tức mà không bị phụ thuộc vào việc tạo tài khoản Google Cloud Console:
  - Chấp nhận token mẫu: `mock-google-token` (hoặc `mock-google:email@gmail.com:Họ Tên`).
  - Tự động trích xuất profile giả lập an toàn để test luồng cấp phát JWT Token.

#### 2. Chính sách Bảo mật Tài khoản Tách biệt (Account Security Policy)
- [x] **Chống chiếm đoạt tài khoản:** Nếu email trả về từ Google đã được đăng ký bằng phương thức mật khẩu truyền thống trước đó, hệ thống sẽ **từ chối đăng nhập và trả về mã lỗi `HTTP 409 Conflict`**: *"Email này đã được đăng ký bằng phương thức mật khẩu. Vui lòng đăng nhập bằng mật khẩu."*
- [x] **Tự động tạo tài khoản Customer:** Nếu là khách hàng hoàn toàn mới, hệ thống tự động tạo tài khoản với `role=customer`, `is_verified=True`, `password_hash=None` (không mật khẩu) và cập nhật avatar từ Google.
- [x] **Cấp phát JWT Token chuẩn:** Trả về cặp JWT Access Token (7 ngày) + Refresh Token (30 ngày).

#### 3. API Endpoint chuẩn OpenAPI Contract (`POST /api/v1/auth/google`)
- [x] **`POST /api/v1/auth/google`:** Nhận `id_token`, xác minh với Google, tự động đăng nhập/đăng ký và trả về `AuthTokenResponse`.

### [Sprint 2 - Task 1] API Giỏ hàng & Validate biến thể tồn kho (Cart & Variant Validation) — *Hoàn thành (30/10/2026)*

#### 1. Mô hình dữ liệu & Migration (`database/migrations/005_cart_items.sql`)
- [x] **Bảng `cart_items` chuẩn UUID:**
  - Khóa chính `id UUID DEFAULT gen_random_uuid()`.
  - Khóa ngoại `user_id UUID REFERENCES users(id) ON DELETE CASCADE`.
  - Khóa ngoại `variant_id UUID REFERENCES product_variants(id) ON DELETE CASCADE`.
  - Số lượng `quantity INT NOT NULL CHECK (quantity > 0)`.
  - Ràng buộc toàn vẹn `UNIQUE(user_id, variant_id)` đảm bảo mỗi biến thể chỉ xuất hiện 1 dòng duy nhất trong giỏ hàng của từng khách hàng (phục vụ cơ chế Upsert).
  - Tự động ghi nhận mốc thời gian `created_at` và `updated_at`.
  - Đánh Index hiệu năng cao: `idx_cart_items_user_id` và `idx_cart_items_variant_id`.

#### 2. Tầng Nghiệp vụ Giỏ hàng (`backend/app-api/app/services/cart/service.py`)
- [x] **Tính toán giá và tồn kho thời gian thực (`get_user_cart`):**
  - Chống gian lận thay đổi giá phía client bằng cách luôn truy vấn trực tiếp giá mới nhất từ bảng `products.price_vnd`.
  - Tồn kho khả dụng được tính theo công thức kép: `stock_available = stock_on_hand - reserved_quantity`.
  - Tự động gắn cờ `is_available = true/false` và cung cấp lý do rõ ràng (`unavailable_reason`):
    - Sản phẩm/danh mục đã ngừng kinh doanh (`product.is_active = false` hoặc `category.is_active = false`).
    - Sản phẩm đã hết hàng (`stock_available <= 0`).
    - Số lượng trong giỏ vượt quá tồn kho khả dụng còn lại (`quantity > stock_available`).
  - Tổng tiền `subtotal_vnd` chỉ tính trên các mặt hàng hợp lệ và khả dụng (`is_available = true`).
- [x] **Cơ chế Upsert thông minh (`add_to_cart`):**
  - Tự động kiểm tra nếu biến thể đã có trong giỏ -> cộng dồn số lượng mới vào số lượng cũ thay vì tạo dòng mới.
  - Kiểm tra giới hạn: số lượng hợp lệ (1 - 100) và không vượt quá tồn kho khả dụng hiện tại.
  - Báo lỗi `409 Conflict` (`OUT_OF_STOCK`) nếu số lượng yêu cầu vượt quá tồn kho khả dụng.
  - Báo lỗi `400 Bad Request` (`PRODUCT_INACTIVE`) nếu sản phẩm đã ngừng kinh doanh.
- [x] **Cập nhật & Xóa sản phẩm (`update_cart_item`, `remove_cart_item`, `clear_user_cart`):**
  - Linh hoạt hỗ trợ tra cứu theo `variant_id` hoặc `cart_item_id` để tiện cho cả Web và Mobile.
  - Xóa 1 biến thể cụ thể khỏi giỏ (`HTTP 204 No Content`).
  - Xóa sạch toàn bộ giỏ hàng của khách hàng sau khi thanh toán/tạo đơn thành công (`HTTP 204 No Content`).

#### 3. Bộ API Giỏ hàng chuẩn RESTful (`/api/v1/cart/*`)
- [x] **`GET /api/v1/cart`:** Lấy chi tiết giỏ hàng hiện tại kèm trạng thái khả dụng của từng món.
- [x] **`POST /api/v1/cart/items`:** Thêm/cộng dồn biến thể vào giỏ hàng (`HTTP 201 Created`).
- [x] **`PATCH /api/v1/cart/items/{variant_id}`:** Cập nhật số lượng của một biến thể (`HTTP 200 OK`).
- [x] **`DELETE /api/v1/cart/items/{variant_id}`:** Xóa 1 biến thể khỏi giỏ (`HTTP 204 No Content`).
- [x] **`DELETE /api/v1/cart`:** Xóa sạch toàn bộ giỏ hàng của user (`HTTP 204 No Content`).
- [x] **Bảo mật phân quyền:** Bắt buộc token xác thực vai trò khách hàng (`require_roles('customer')`).

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_cart.py`)
- [x] **Đạt 100% Passed 8 test cases với `unittest` & `TestClient`:**
  1. `test_01_add_valid_variant_to_cart_success`: Thêm biến thể hợp lệ -> Trả về `201 Created`, đầy đủ trường và tổng tiền.
  2. `test_02_upsert_accumulate_quantity`: Thêm biến thể đã có trong giỏ -> Tự động cộng dồn số lượng chính xác.
  3. `test_03_add_variant_exceeding_stock_fails`: Thêm số lượng vượt tồn kho -> Báo lỗi `409 Conflict (OUT_OF_STOCK)`.
  4. `test_04_update_quantity_invalid`: Cập nhật số lượng `<= 0` -> Báo lỗi `422 Unprocessable Entity (VALIDATION_ERROR)`.
  5. `test_05_inactive_product_marked_unavailable_in_cart`: Sản phẩm cha bị ẩn (`is_active=false`) -> Đánh dấu `is_available=false` kèm lý do ngừng kinh doanh.
  6. `test_06_delete_cart_item`: Xóa 1 biến thể khỏi giỏ -> Trả về `204 No Content`.
  7. `test_07_clear_entire_cart`: Xóa sạch giỏ hàng -> Trả về `204 No Content`.
  8. `test_08_update_valid_quantity_success`: Cập nhật số lượng hợp lệ trong kho -> Trả về `200 OK`.

### [Sprint 2 - Task 2] Tích hợp Cổng thanh toán VNPay Sandbox (Create URL, IPN Webhook & Return URL) — *Hoàn thành (30/10/2026)*

#### 1. Cấu hình Cổng thanh toán (`app/services/payments/vnpay.py`)
- [x] **Tham số môi trường chuẩn VNPay Sandbox 2.1.0:**
  - `VNPAY_TMN_CODE`: Mã định danh điểm bán hàng test (`2QXUI4J4`).
  - `VNPAY_HASH_SECRET`: Khóa bí mật dùng cho thuật toán ký số HMAC-SHA512 (`RAIQUND2GHRLKTUTZLPHXD2XFXA53MNN`).
  - `VNPAY_URL`: Cổng thanh toán Sandbox (`https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`).
  - `VNPAY_RETURN_URL`: Đường dẫn nhận redirect trình duyệt sau giao dịch (`http://localhost:8000/api/v1/payments/vnpay/return`).

#### 2. Tầng Nghiệp vụ VNPay (`backend/app-api/app/services/payments/vnpay.py`)
- [x] **Thuật toán sinh chữ ký HMAC-SHA512 (`generate_vnpay_signature`, `verify_vnpay_signature`):**
  - Lọc toàn bộ tham số bắt đầu bằng `vnp_` (loại bỏ `vnp_SecureHash` và `vnp_SecureHashType`).
  - Sắp xếp thứ tự alphabet các keys.
  - Mã hóa URL theo chuẩn RFC 3986 với `urllib.parse.quote_plus`.
  - Tạo chữ ký HMAC-SHA512 bằng khóa bí mật `VNPAY_HASH_SECRET`.
  - Đối chiếu chữ ký bảo mật an toàn bằng `hmac.compare_digest` chống tấn công Timing Attack.
- [x] **Tạo URL thanh toán (`create_vnpay_payment_url`):**
  - Kiểm tra đơn hàng tồn tại, thuộc quyền sở hữu của khách hàng.
  - Validate đơn hàng có phương thức thanh toán là `vnpay` và trạng thái `pending_confirmation`.
  - Kiểm tra thời hạn giữ chỗ: Nếu `hold_expires_at <= now()` -> Báo lỗi `409 HOLD_EXPIRED`.
  - Nhân số tiền x100 theo chuẩn VNPay: `vnp_Amount = total_vnd * 100`.
  - Sinh URL chuyển hướng chứa chữ ký số hợp lệ và thời hạn giao dịch 15 phút.
- [x] **Xử lý Webhook IPN Server-to-Server (`process_vnpay_ipn`):**
  - **Bước 1 (Xác minh chữ ký):** Kiểm tra hash HMAC-SHA512. Sai -> Trả ngay `{"RspCode": "97", "Message": "Invalid Checksum"}`.
  - **Bước 2 (Tra cứu đơn hàng):** Tìm đơn theo `order_number = vnp_TxnRef` có khóa hàng `FOR UPDATE`. Không tìm thấy -> Trả `{"RspCode": "01", "Message": "Order Not Found"}`.
  - **Bước 3 (Đối chiếu số tiền):** So sánh `vnp_Amount / 100 == order.total_vnd`. Sai -> Trả `{"RspCode": "04", "Message": "Invalid Amount"}`.
  - **Bước 4 (Chống xử lý trùng lặp - Idempotency):** Nếu đơn đã `confirmed` hoặc `payment_status == 'paid'` -> Trả ngay `{"RspCode": "02", "Message": "Order already confirmed"}` và tuyệt đối không trừ kho 2 lần.
  - **Bước 5 (Khấu trừ tồn kho & Xác nhận đơn hàng):**
    - Khi `vnp_ResponseCode == "00"`: Tự động trừ kho thực tế `stock_on_hand -= quantity`, trừ giữ chỗ `reserved_quantity -= quantity`, đổi trạng thái đặt chỗ sang `consumed`, ghi nhật ký `inventory_adjustments`, cập nhật `orders.status = 'confirmed'`, `orders.payment_status = 'paid'`, giải phóng `hold_expires_at = NULL`.
    - Phản hồi cho VNPay: `{"RspCode": "00", "Message": "Confirm Success"}`.
- [x] **Xử lý Trình duyệt Return URL (`process_vnpay_return`):**
  - Tiếp nhận kết quả thanh toán khi khách hàng quay lại ứng dụng/web.
  - Xác thực chữ ký và trả về payload có cấu trúc `is_success`, `order_number`, `amount_vnd`, `transaction_no`, `message` thân thiện để hiển thị UI.

#### 3. Bộ API Thanh toán RESTful (`/api/v1/payments/vnpay/*`)
- [x] **`POST /api/v1/payments/vnpay/create-url`:** Sinh URL thanh toán cho đơn hàng (Bảo mật: yêu cầu vai trò `customer`).
- [x] **`GET /api/v1/payments/vnpay/ipn`:** Webhook nhận callback ngầm từ VNPay (Public IPN endpoint).
- [x] **`GET /api/v1/payments/vnpay/return`:** Trang tiếp nhận redirect người dùng sau khi thanh toán.

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_vnpay.py`)
- [x] **Đạt 100% Passed 6 test cases chuyên biệt:**
  1. `test_01_create_vnpay_url_success`: Sinh URL thanh toán VNPay đầy đủ tham số và chữ ký HMAC-SHA512 chuẩn.
  2. `test_02_ipn_success_confirm_order_and_deduct_stock`: IPN thành công (`vnp_ResponseCode="00"`) -> Đơn đổi sang `confirmed`, `payment_status="paid"`, tồn kho thực tế bị khấu trừ và reservation sang `consumed`.
  3. `test_03_ipn_invalid_signature_returns_97`: IPN giả mạo chữ ký -> Báo lỗi `RspCode: "97" (Invalid Checksum)`, đơn hàng không bị thay đổi.
  4. `test_04_ipn_invalid_amount_returns_04`: IPN sai lệch số tiền -> Báo lỗi `RspCode: "04" (Invalid Amount)`.
  5. `test_05_ipn_idempotency_returns_02_and_no_double_deduction`: Gọi IPN 2 lần liên tiếp cho cùng 1 đơn -> Lần 2 trả `RspCode: "02" (Order already confirmed)`, kho không bị trừ 2 lần.
  6. `test_06_vnpay_return_endpoint`: Kiểm tra return URL xác thực chữ ký và tóm tắt giao dịch cho Frontend.

### [Sprint 2 - Task 3] API Bán hàng & Thanh toán tại quầy (Counter Order: Cash & VietQR Napas 247) — *Hoàn thành (30/10/2026)*

#### 1. Phân quyền & Mô hình Đơn tại quầy
- [x] **Phân quyền truy cập nghiêm ngặt:** Chỉ nhân viên bán hàng (`sales_staff`) hoặc quản trị viên (`admin`) mới được phép truy cập (`require_roles("sales_staff", "admin")`). Chặn đứng mọi nỗ lực gọi trái phép từ tài khoản `customer` (`HTTP 403 Forbidden`).
- [x] **Mô hình đơn hàng tại quầy (`order_type = 'counter'`):**
  - Hỗ trợ bán hàng cho cả khách vãng lai (`customer_id = None`) và khách hàng thành viên có tài khoản.
  - Snapshot địa chỉ tự động gán nhãn `in_store_counter`.

#### 2. Tầng Nghiệp vụ Bán hàng tại quầy (`backend/app-api/app/services/sales/service.py`)
- [x] **Tạo đơn hàng tại quầy (`create_counter_order`):**
  - Tạo đơn và giữ chỗ hàng trong kho tạm thời (`status = 'pending_confirmation'`).
- [x] **Thanh toán tiền mặt (`pay_order_cash`):**
  - Nhận số tiền mặt khách đưa (`cash_received`).
  - Kiểm tra `cash_received >= order.total_vnd`. Nếu thiếu -> Trả lỗi `400 Bad Request (INVALID_CASH_AMOUNT)`.
  - Tự động tính tiền thối/tiền thừa chính xác: `cash_change = cash_received - order.total_vnd`.
  - Khấu trừ kho thực tế ngay lập tức thông qua `confirm_order()`, giải phóng giữ chỗ và chuyển trạng thái đặt chỗ sang `consumed`.
  - Cập nhật trạng thái đơn: `status = 'completed'`, `payment_status = 'paid'`, `payment_method = 'cash'`.
  - Ghi nhật ký chi tiết vào `order_status_history` gồm số tiền nhận, tiền thừa và mã nhân viên thu ngân.
- [x] **Sinh mã VietQR Napas 247 chuẩn quốc tế (`generate_vietqr_payload`):**
  - Tự động lấy cấu hình ngân hàng thụ hưởng (Mã BIN VietQR, Số tài khoản, Tên chủ tài khoản).
  - Tự động gắn nội dung chuyển khoản là mã đơn hàng (`order_number`) và số tiền chuẩn `total_vnd`.
  - Sinh URL ảnh QR động từ cổng VietQR QuickLink (`https://img.vietqr.io/image/...`).
  - Tích hợp hàm sinh chuỗi mã QR chuẩn **EMVCo / Napas 247** kèm thuật toán tính checksum **CRC16-CCITT** giúp hỗ trợ máy quét POS và ứng dụng render offline.
- [x] **Xác nhận chuyển khoản tại quầy (`confirm_bank_transfer`):**
  - Nhân viên quầy xác nhận tiền đã vào tài khoản cửa hàng.
  - Tự động khấu trừ kho, chuyển đơn sang `completed`, `payment_status = 'paid'`, `payment_method = 'bank_transfer'`.

#### 3. Bộ API Chuẩn RESTful (`/api/v1/sales/orders/*`)
- [x] **`POST /api/v1/sales/orders`:** Tạo đơn hàng bán trực tiếp tại quầy (`HTTP 201 Created`).
- [x] **`POST /api/v1/sales/orders/{order_id}/pay-cash`:** Thanh toán tiền mặt, tính tiền thừa và hoàn tất đơn (`HTTP 200 OK`).
- [x] **`POST /api/v1/sales/orders/{order_id}/vietqr`:** Sinh mã QR chuyển khoản ngân hàng VietQR (`HTTP 200 OK`).
- [x] **`POST /api/v1/sales/orders/{order_id}/confirm-transfer`:** Xác nhận nhận tiền chuyển khoản và hoàn tất đơn (`HTTP 200 OK`).

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_sales.py`)
- [x] **Đạt 100% Passed 6 test cases chuyên biệt:**
  1. `test_01_create_counter_order_success`: Tạo đơn quầy thành công -> Trả về `201 Created` với `order_type = 'counter'`.
  2. `test_02_pay_cash_success_and_correct_change`: Thanh toán tiền mặt đủ -> Trả về tiền thừa chính xác, đơn chuyển `completed`, kho thực tế bị khấu trừ.
  3. `test_03_pay_cash_insufficient_fails_400`: Khách đưa thiếu tiền -> Báo lỗi `400 Bad Request (INVALID_CASH_AMOUNT)`, kho không bị trừ.
  4. `test_04_vietqr_payload_matches_order`: Sinh VietQR chứa đúng mã đơn, đúng số tiền, sinh link ảnh và chuỗi EMVCo hợp lệ.
  5. `test_05_confirm_bank_transfer_success`: Xác nhận chuyển khoản thành công -> Đơn hoàn tất `completed`, phương thức `bank_transfer`, kho bị trừ.
  6. `test_06_customer_forbidden_from_sales_api`: Tài khoản `customer` cố tình gọi API sales -> Bị chặn đứng với `403 Forbidden`.

### [Sprint 2 - Task 4] API Đơn hàng COD & Xác nhận Đối soát Thu tiền (Cash on Delivery) — *Hoàn thành (30/10/2026)*

#### 1. Quy tắc Nghiệp vụ Đơn hàng COD
- [x] **Điều kiện tạo đơn COD (`payment_method = 'cod'`):**
  - Khách hàng bắt buộc cung cấp đầy đủ thông tin giao hàng trong `shipping_address`: họ tên người nhận (`name`), số điện thoại liên hệ (`phone`), và địa chỉ chi tiết (`address`).
  - Đơn COD được tự động duyệt chuyển thẳng sang trạng thái `orders.status = 'confirmed'` (đã duyệt đơn giao hàng), kho thực tế được khấu trừ ngay lập tức, và trạng thái thanh toán ban đầu là `orders.payment_status = 'unpaid'`.

#### 2. Tầng Nghiệp vụ Đối soát Thu tiền COD (`backend/app-api/app/services/orders/service.py`)
- [x] **Quy trình thu tiền COD an toàn (`collect_cod_payment`):**
  - **Phân quyền:** Dành riêng cho nhân viên kho (`warehouse_staff`), nhân viên thu ngân (`sales_staff`) hoặc quản trị viên (`admin`). Khách hàng `customer` bị chặn với `403 Forbidden`.
  - **Kiểm tra phương thức:** Chỉ cho phép đơn hàng có `payment_method == 'cod'`.
  - **Kiểm tra trạng thái hợp lệ:** Đơn hàng bắt buộc phải ở trạng thái đang giao (`shipped`) hoặc đã giao thành công (`completed`). Nếu đơn còn ở `pending_confirmation` hoặc `processing` -> Từ chối báo lỗi `400 Bad Request (INVALID_ORDER_STATE)`.
  - **Chống đối soát trùng lặp (Idempotent):** Kiểm tra `orders.payment_status == 'unpaid'`. Nếu đơn đã là `'paid'` -> Báo lỗi `409 Conflict (ORDER_ALREADY_PAID)`.
  - **Ghi nhận lịch sử giao dịch:** Cập nhật `orders.payment_status = 'paid'`, tự động ghi vết nhân viên thực hiện đối soát và số tiền thu vào bảng `order_status_history`.

#### 3. Bộ API Chuẩn RESTful (`/api/v1/orders/*`)
- [x] **`POST /api/v1/orders`:** Hỗ trợ tạo đơn hàng COD trực tiếp với `confirm_immediately = True` khi `payment_method = 'cod'`.
- [x] **`POST /api/v1/orders/{order_id}/cod-collect`:** Xác nhận đối soát thu tiền COD (Role: `warehouse_staff`, `sales_staff`, `admin`).

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_cod.py`)
- [x] **Đạt 100% Passed 5 test cases chuyên biệt:**
  1. `test_01_create_cod_order_success`: Tạo đơn COD hợp lệ -> Trạng thái `status = 'confirmed'`, `payment_status = 'unpaid'`, kho bị trừ thực tế.
  2. `test_02_cod_collect_when_processing_fails_400`: Thu COD khi đơn đang đóng gói (`processing`) -> Báo lỗi `400 Bad Request (INVALID_ORDER_STATE)`.
  3. `test_03_cod_collect_when_completed_success`: Thu COD khi đơn đã giao (`completed`) -> Cập nhật thành công sang `paid`.
  4. `test_04_cod_collect_duplicate_fails_409`: Thu COD lần thứ 2 cho cùng 1 đơn -> Báo lỗi `409 Conflict (ORDER_ALREADY_PAID)`.
  5. `test_05_customer_forbidden_from_cod_collect`: Tài khoản `customer` gọi thu COD -> Bị chặn với `403 Forbidden`.

### [Sprint 2 - Task 5] API Xử lý Đóng gói & Giao nhận (Fulfillment State Machine) — *Hoàn thành (30/10/2026)*

#### 1. Phân quyền & Mô hình Vận hành Kho
- [x] **Phân quyền chặt chẽ:** Chỉ nhân viên kho (`warehouse_staff`) hoặc quản trị viên (`admin`) mới được phép truy cập (`require_roles("warehouse_staff", "admin")`). Chặn đứng mọi nỗ lực gọi trái phép từ tài khoản `customer` hoặc các vai trò khác (`HTTP 403 Forbidden`).

#### 2. Tầng Nghiệp vụ Đóng gói & Giao nhận (`backend/app-api/app/services/warehouse/service.py`)
- [x] **Truy vấn danh sách đơn soạn hàng (`list_warehouse_orders`):**
  - Hỗ trợ lọc đa tiêu chí: `status` (mặc định các đơn `confirmed` chờ chuẩn bị), `order_type` (`online` hoặc `counter`), `date` (ngày đặt hàng).
  - Sắp xếp chuẩn FIFO (`created_at ASC`): Đơn đặt trước được chuẩn bị và xuất kho trước.
  - Phân trang chuẩn kèm tổng số lượng và chi tiết các mặt hàng snapshot trong từng đơn.
- [x] **Máy trạng thái Đóng gói & Vận chuyển nghiêm ngặt (Fulfillment State Machine) (`update_fulfillment_status`):**
  - **Quy trình tuần tự bắt buộc:**
    - **Bước 1 (Bắt đầu soạn hàng):** `confirmed` -> `processing`
    - **Bước 2 (Đóng gói xong, chờ ship):** `processing` -> `ready_to_ship`
    - **Bước 3 (Bàn giao vận chuyển):** `ready_to_ship` -> `shipped`
      - **Validate nghiệp vụ:** Khi chuyển sang `shipped`, payload **bắt buộc** phải có `carrier_name` (đơn vị vận chuyển: GHN, GHTK, ViettelPost...) và `tracking_code` (mã vận đơn). Thiếu 1 trong 2 sẽ lập tức trả lỗi `422 Unprocessable Entity`.
      - Tự động cập nhật `carrier_name` và `tracking_code` vào `address_snapshot` của đơn hàng.
    - **Bước 4 (Giao thành công):** `shipped` -> `completed`
  - **Chống nhảy cóc trạng thái:** Mọi hành vi bỏ qua các bước tuần tự (ví dụ từ `confirmed` nhảy cóc lên `completed` hoặc `ready_to_ship`) đều bị chặn và trả lỗi `409 Conflict (ORDER_STATE_CONFLICT)`.
  - **Ghi nhật ký lịch sử đơn hàng:** Tự động ghi vết đầy đủ vào bảng `order_status_history` gồm `from_status`, `to_status`, `changed_by` (nhân viên kho) và ghi chú vận đơn.

#### 3. Bộ API Chuẩn RESTful (`/api/v1/warehouse/orders/*`)
- [x] **`GET /api/v1/warehouse/orders`:** Lấy danh sách đơn hàng cần đóng gói & giao nhận (Role: `warehouse_staff`, `admin`).
- [x] **`PATCH /api/v1/warehouse/orders/{order_id}/status`:** Chuyển trạng thái quy trình xử lý đơn hàng theo máy trạng thái tuần tự.

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_warehouse.py`)
- [x] **Đạt 100% Passed 5 test cases chuyên biệt:**
  1. `test_01_get_warehouse_orders_list`: Lấy danh sách đơn cần soạn hàng `confirmed` thành công kèm thông tin chi tiết sản phẩm.
  2. `test_02_fulfillment_step_by_step_transitions`: Thực thi tuần tự 4 bước (`confirmed` -> `processing` -> `ready_to_ship` -> `shipped` -> `completed`) thành công và lưu mã vận đơn.
  3. `test_03_jump_state_fails_409_state_conflict`: Cố tình nhảy cóc trạng thái -> Báo lỗi `409 Conflict (ORDER_STATE_CONFLICT)`.
  4. `test_04_shipped_missing_tracking_code_fails_422`: Chuyển sang `shipped` nhưng thiếu mã vận đơn hoặc đơn vị vận chuyển -> Báo lỗi `422 Unprocessable Entity`.
  5. `test_05_customer_forbidden_from_warehouse_api`: Tài khoản `customer` cố tình truy cập API kho -> Bị chặn với `403 Forbidden`.

### [Sprint 2 - Task 6] Đối soát Giao dịch Định kỳ & QueryDR VNPay (Reconciliation Worker) — *Hoàn thành (30/10/2026)*

#### 1. Cơ chế Chạy nền & Kiểm soát Đụng độ (Concurrency Control)
- [x] **Tiến trình ngầm tự động (Background Worker):**
  - Tự động kích hoạt khi FastAPI khởi động (`startup_event`) và giải phóng tài nguyên an toàn khi tắt ứng dụng (`shutdown_event`).
  - Chạy quét định kỳ chu kỳ mỗi 5 phút (300 giây) đối soát các giao dịch treo trên hệ thống.
- [x] **Tiêu chí lọc đơn hàng cần đối soát:**
  - `payment_method = 'vnpay'`
  - `status = 'pending_confirmation'`
  - `payment_status = 'unpaid'`
  - Thời gian tạo đơn đã trôi qua quá 10 phút (`created_at <= now() - INTERVAL '10 minutes'`) để đảm bảo khách đã có thời gian thanh toán.
- [x] **Khóa chống đụng độ cấp cơ sở dữ liệu (`FOR UPDATE SKIP LOCKED`):**
  - Sử dụng cơ chế khóa dòng của PostgreSQL: Nếu máy chủ VNPay đồng thời gửi Webhook IPN về và giữ khóa đơn hàng, worker sẽ **tự động bỏ qua (SKIP LOCKED)** hàng đó, ngăn chặn triệt để tình trạng Deadlock hoặc xử lý đè lẫn nhau.

#### 2. Tầng Nghiệp vụ QueryDR VNPay (`backend/app-api/app/services/payments/reconciliation.py`)
- [x] **Tích hợp API truy vấn kết quả giao dịch VNPay v2.1.0 (`querydr`):**
  - Chuẩn hóa chuỗi hash: `requestId|version|command|tmnCode|txnRef|txnDate|createDate|ipAddr|orderInfo` mã hóa HMAC-SHA512.
  - Gửi request an toàn tới endpoint VNPay Sandbox: `https://sandbox.vnpayment.vn/merchant_webapi/api/transaction`.
- [x] **Xử lý kết quả & Khấu trừ kho tự động:**
  - Nếu kết quả từ ngân hàng/VNPay là **Đã thanh toán thành công (`vnp_ResponseCode == "00"` và `vnp_TransactionStatus == "00"`)**:
    - Gọi hàm `confirm_order()`: Tự động khấu trừ kho thực tế `stock_on_hand -= quantity`, giải phóng giữ chỗ `reserved_quantity -= quantity`, đổi đặt chỗ sang `consumed`.
    - Cập nhật `orders.status = 'confirmed'`, `orders.payment_status = 'paid'`.
    - Ghi log vết lịch sử: *"Reconciliation worker: Confirmed order via QueryDR"*.
- [x] **Cơ chế Exponential Backoff & Chống lặp vô hạn:**
  - Giới hạn tối đa 3 lần thử truy vấn cho mỗi đơn hàng (lưu vết trong metadata `address_snapshot`). Nếu quá 3 lần đơn vẫn chưa thanh toán, worker sẽ dừng truy vấn để tránh lãng phí tài nguyên hệ thống.

#### 3. API Kích hoạt Thủ công (`POST /api/v1/payments/vnpay/reconcile`)
- [x] **`POST /api/v1/payments/vnpay/reconcile`:** Cho phép quản trị viên hoặc nhân viên kho/thu ngân kích hoạt batch đối soát ngay lập tức khi cần thiết (Role: `warehouse_staff`, `sales_staff`, `admin`).

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_reconciliation.py`)
- [x] **Đạt 100% Passed 5 test cases chuyên biệt:**
  1. `test_01_worker_scans_only_orders_older_than_10_minutes`: Worker chỉ quét các đơn tạo quá 10 phút, bỏ qua đơn mới tạo.
  2. `test_02_querydr_success_confirms_order_and_deducts_stock`: QueryDR phản hồi `00` -> Tự động xác nhận đơn, đổi `payment_status = 'paid'`, khấu trừ kho thực tế.
  3. `test_03_already_paid_order_not_scanned_again`: Đơn đã thanh toán không bị quét lại.
  4. `test_04_concurrency_skip_locked`: Kiểm tra cơ chế khóa chống xung đột giữa worker và IPN với `FOR UPDATE SKIP LOCKED`.
  5. `test_05_reconciliation_api_endpoint_rbac`: Kiểm tra phân quyền gọi API đối soát thủ công (Admin được phép, Customer bị chặn 403).

### [Sprint 2 - Task 7] API Hoàn tiền & Hoàn trả Tồn kho (Refund & Restock) — *Hoàn thành (30/10/2026)*

#### 1. Nghiệp vụ & Điều kiện Hoàn tiền (Refund Business Logic)
- [x] **Phân quyền truy cập nghiêm ngặt:** Chỉ tài khoản có vai trò `admin` (`require_roles("admin")`) mới được phép kích hoạt hoàn tiền và hoàn kho. Các tài khoản người dùng bình thường (`customer`) hoặc nhân viên kho/thu ngân không có thẩm quyền đều bị chặn với mã lỗi `403 Forbidden`.
- [x] **Quy tắc kiểm định trạng thái đơn hàng (Validation Guards):**
  - **Đơn bắt buộc phải đã thanh toán:** `orders.payment_status == 'paid'`. Nếu đơn chưa thanh toán (`unpaid`), từ chối với mã lỗi `400 Bad Request` (`ORDER_NOT_PAID`).
  - **Chống hoàn tiền trùng lặp (Idempotency):** Nếu đơn đã hoàn tiền trước đó (`orders.payment_status == 'refunded'`), từ chối với mã lỗi `409 Conflict` (`ORDER_ALREADY_REFUNDED`).
  - **Kiểm tra số tiền hoàn:** `refund_amount <= orders.total_vnd` (nếu không truyền `refund_amount`, mặc định hoàn 100% giá trị đơn hàng).

#### 2. Nghiệp vụ Hoàn trả Tồn kho Tự động (Restock Logic)
- [x] **Hồi phục tồn kho thực tế (`product_variants.stock_on_hand`):**
  - Quét từng dòng sản phẩm trong `order_items` với khóa dòng `FOR UPDATE` trên `product_variants`.
  - Tự động cộng trả lại chính xác số lượng (`stock_on_hand += item.quantity`).
- [x] **Giải phóng giữ chỗ kho (`inventory_reservations`):**
  - Chuyển toàn bộ các bản ghi giữ chỗ liên quan sang trạng thái `'released'`, giải phóng hoàn toàn tài nguyên.
- [x] **Ghi nhật ký điều chỉnh kho (`inventory_adjustments`):**
  - Tự động tạo bản ghi đối soát lịch sử tồn kho với:
    - `delta = +item.quantity`
    - `quantity_before = current_stock`
    - `quantity_after = current_stock + item.quantity`
    - `reason = "Order {order_number} refunded & restocked by Admin"`
    - `changed_by = admin_id`

#### 3. Cập nhật Trạng thái & Lưu vết Lịch sử Đơn hàng
- [x] **Cập nhật đơn hàng:**
  - `orders.status = 'cancelled'`
  - `orders.payment_status = 'refunded'`
  - `orders.cancelled_at = now()`
  - Lưu chi tiết hoàn tiền vào metadata `address_snapshot`: `refund_amount`, `refund_reason`, `refunded_by`, `refunded_at`.
- [x] **Ghi vết lịch sử chuyển đổi (`order_status_history`):**
  - Ghi nhận `from_status = order.status`, `to_status = 'cancelled'`.
  - Ghi chú: `"Hoàn tiền {refund_amount:,} VND bởi Admin. Lý do: {reason}"`.

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_refund.py`)
- [x] **Đạt 100% Passed 5 test cases nghiệp vụ:**
  1. `test_admin_refund_paid_order_success`: Admin hoàn tiền đơn đã thanh toán -> `payment_status='refunded'`, `status='cancelled'`, ghi nhận vết lịch sử.
  2. `test_restock_inventory_restored`: Kiểm tra chính xác tồn kho `stock_on_hand` được hồi phục đầy đủ và ghi log `inventory_adjustments`.
  3. `test_refund_unpaid_order_fails`: Hoàn tiền cho đơn chưa thanh toán -> Báo lỗi `400 Bad Request` (`ORDER_NOT_PAID`).
  4. `test_refund_already_refunded_order_fails`: Cố tình gọi hoàn tiền lần 2 -> Báo lỗi `409 Conflict` (`ORDER_ALREADY_REFUNDED`).
  5. `test_non_admin_cannot_refund`: User không phải admin gọi hoàn tiền -> Báo lỗi `403 Forbidden`.

### [Sprint 2 - Task 8] Job Tự động Hủy Đơn Quá hạn Giữ chỗ (Auto-Cancel Expired Orders) — *Hoàn thành (31/10/2026)*

#### 1. Cơ chế Chạy nền & Điều kiện Quét Đơn (Background Cron Job)
- [x] **Tiến trình ngầm tự động (Expiration Worker):**
  - Tự động kích hoạt khi FastAPI khởi động (`startup_event`) và giải phóng tài nguyên an toàn khi tắt ứng dụng (`shutdown_event`).
  - Chạy quét định kỳ chu kỳ mỗi 5 phút (300 giây) xử lý các đơn hàng online thanh toán qua cổng điện tử bị quá hạn giữ chỗ.
- [x] **Điều kiện xác định đơn hàng quá hạn:**
  - `orders.status == 'pending_confirmation'`
  - `orders.hold_expires_at <= now()` (đã hết 15 phút giữ chỗ kho tạm thời mà khách hàng không hoàn tất thanh toán VNPay).
- [x] **Khóa chống tranh chấp giao dịch (Concurrency Control):**
  - Sử dụng cơ chế khóa PostgreSQL `ORDER BY hold_expires_at LIMIT :limit FOR UPDATE SKIP LOCKED` để tránh khóa chết (deadlock) hoặc tranh chấp khi có nhiều worker xử lý đồng thời.

#### 2. Quy trình Hủy đơn & Thu hồi Tồn kho Giữ chỗ (Release Reservation)
- [x] **Hủy trạng thái đơn hàng:**
  - Chuyển `orders.status = 'expired'`.
  - Xóa thời hạn giữ chỗ: `orders.hold_expires_at = NULL`.
- [x] **Giải phóng giữ chỗ kho tự động (`inventory_reservations` & `product_variants`):**
  - Trừ ngược số lượng giữ chỗ: `product_variants.reserved_quantity -= reservation.quantity`.
  - Nhờ đó, số tồn kho khả dụng (`stock_on_hand - reserved_quantity`) được hồi phục nguyên vẹn ngay lập tức để phục vụ cho các khách hàng khác tiếp tục đặt mua.
  - Cập nhật trạng thái giữ chỗ sang `'released'`: `inventory_reservations.status = 'released'`.
- [x] **Lưu vết lịch sử đơn hàng (`order_status_history`):**
  - Ghi nhận `from_status = 'pending_confirmation'`, `to_status = 'expired'`.
  - Ghi chú: `"Inventory hold expired after 15 minutes"`.

#### 3. API Kích hoạt Thủ công (`POST /api/v1/admin/orders/expire-stale`)
- [x] **`POST /api/v1/admin/orders/expire-stale`:** Cho phép quản trị viên hoặc nhân viên kho kích hoạt kiểm tra và hủy đơn quá hạn ngay lập tức (Role: `admin`, `warehouse_staff`).

#### 4. Bộ Kiểm thử tự động (Unit Tests) (`backend/app-api/tests/unit/test_expiration.py`)
- [x] **Đạt 100% Passed 5 test cases chuyên biệt:**
  1. `test_01_stale_order_auto_expired`: Đơn hàng VNPay quá hạn 15 phút tự động chuyển sang `status='expired'`, xóa `hold_expires_at` và ghi nhận lịch sử.
  2. `test_02_inventory_reservation_released`: Kiểm tra chính xác `reserved_quantity` được giải phóng về 0, tồn kho khả dụng tăng lại tương ứng.
  3. `test_03_active_unexpired_order_not_cancelled`: Đơn hàng còn trong thời hạn 15 phút giữ chỗ không bị hủy nhầm.
  4. `test_04_confirmed_and_cod_orders_not_cancelled`: Đơn hàng đã thanh toán (`confirmed`) hoặc đơn COD không bị quét hủy.
  5. `test_05_admin_expire_stale_api_endpoint`: Kiểm tra phân quyền gọi API quét đơn quá hạn thủ công (Admin được phép, Customer bị chặn 403).

---

## 🛠 Hướng dẫn cho thành viên nhóm khi kéo code về (Quickstart)

Mọi thành viên sau khi `git clone` hoặc `git pull` nhánh mới về, chỉ cần làm theo các bước sau:

### Bước 1: Chuẩn bị file môi trường
```powershell
# Sao chép từ mẫu biến môi trường
cp .env.example .env
```

### Bước 2: Khởi chạy môi trường với Docker
Yêu cầu: Đã bật **Docker Desktop**.
```powershell
# Build và chạy ngầm toàn bộ dịch vụ (Postgres, Redis, MinIO, API)
docker compose up --build -d

# Xem log thời gian thực của backend
docker compose logs -f app-api
```

### Bước 3: Nạp dữ liệu mẫu & Chạy Migration
Sau khi container đã chạy, bạn chạy lệnh sau để tự động tạo bảng và nạp đầy đủ dữ liệu mẫu:
```powershell
# Cách 1 (Khuyên dùng - chạy trực tiếp trong container Docker):
docker compose exec app-api python -m backend.shared.database.seed

# Hoặc Cách 2 (nếu chạy từ môi trường Python máy host):
python -m backend.shared.database.seed
```
*(Lệnh này idempotent: chạy nhiều lần an toàn, không bị duplicate dữ liệu).*

### Bước 4: Kiểm tra kết nối từ trình duyệt / Postman / Swagger UI
* **Tài liệu API tương tác (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
  - Nhóm **Auth & Phone OTP**:
    - `POST /api/v1/auth/google` -> **Đăng nhập Google:** Truyền `id_token: "mock-google-token"` (hoặc `mock-google:user@gmail.com:Nguyen Van A`) -> Trả về ngay JWT Access Token.
    - `POST /api/v1/auth/otp/send` -> Gửi mã OTP tới SĐT (VD: `0901234567`). Terminal backend sẽ in mã OTP, và response trả kèm `debug_otp`.
    - `POST /api/v1/auth/otp/verify` -> Kiểm tra mã OTP vừa nhận.
    - `POST /api/v1/auth/otp/login` -> Đăng nhập nhanh không cần mật khẩu -> Trả về JWT Access Token.
    - `POST /api/v1/auth/password/reset-with-otp` -> Đặt lại mật khẩu mới bằng OTP.
  - Nhóm **Profile**:
    - `GET /api/v1/users/me` -> Xem hồ sơ cá nhân và số đo AI.
    - `PUT /api/v1/users/me` -> Cập nhật thông tin và số đo.
    - `POST /api/v1/users/me/avatar` -> Tải ảnh đại diện lên MinIO.
  - Nhóm **QR Code**:
    - `GET /api/v1/qr/scan?code=virtufit://product/1` -> Trả về thông tin sản phẩm và phòng thử đồ AI.
  - Nhóm **Catalog & Products**:
    - `GET /catalog/categories` -> Xem cây danh mục.
    - `GET /catalog/products` -> Tìm kiếm và lọc sản phẩm.
    - `GET /catalog/products/1` -> Xem chi tiết sản phẩm.
  - Nhóm **Admin Orders & Expiration (Hoàn tiền & Hủy đơn quá hạn - Sprint 2)**:
    - `POST /api/v1/admin/orders/{order_id}/refund` -> Hoàn tiền đơn hàng đã thanh toán và tự động hoàn trả tồn kho sản phẩm vào `product_variants.stock_on_hand` (Role: `admin`).
    - `POST /api/v1/admin/orders/expire-stale` -> Kích hoạt quét và hủy các đơn hàng quá hạn giữ chỗ 15 phút (Role: `admin`, `warehouse_staff`).
  - Nhóm **Warehouse & Fulfillment (Xử lý Đóng gói & Giao nhận - Sprint 2)**:
    - `GET /api/v1/warehouse/orders` -> Lấy danh sách đơn hàng cần chuẩn bị soạn hàng (Role: `warehouse_staff`, `admin`).
    - `PATCH /api/v1/warehouse/orders/{order_id}/status` -> Chuyển trạng thái tuần tự: `confirmed` -> `processing` -> `ready_to_ship` -> `shipped` -> `completed`.
  - Nhóm **Orders & COD (Đơn hàng & Thu tiền COD - Sprint 2)**:
    - `POST /api/v1/orders` -> Tạo đơn hàng trực tuyến (hỗ trợ `payment_method: "cod"` hoặc `"vnpay"`).
    - `POST /api/v1/orders/{order_id}/cod-collect` -> Đối soát và xác nhận đã thu tiền COD (Role: `warehouse_staff`, `sales_staff`, `admin`).
  - Nhóm **Sales (POS & Quầy - Sprint 2)**:
    - `POST /api/v1/sales/orders` -> Tạo đơn hàng bán trực tiếp tại quầy (Role: `sales_staff`, `admin`).
    - `POST /api/v1/sales/orders/{order_id}/pay-cash` -> Thanh toán tiền mặt, tính tiền thừa và trừ kho.
    - `POST /api/v1/sales/orders/{order_id}/vietqr` -> Sinh mã QR chuyển khoản VietQR Napas 247.
    - `POST /api/v1/sales/orders/{order_id}/confirm-transfer` -> Xác nhận nhận tiền chuyển khoản và hoàn tất đơn.
  - Nhóm **Payments (VNPay Sandbox - Sprint 2)**:
    - `POST /api/v1/payments/vnpay/create-url` -> Sinh URL thanh toán VNPay Sandbox (Payload: `{"order_id": "<UUID>"}`).
    - `GET /api/v1/payments/vnpay/ipn` -> Webhook ngầm nhận callback xác nhận từ VNPay (`{"RspCode": "00", "Message": "Confirm Success"}`).
    - `GET /api/v1/payments/vnpay/return` -> Tiếp nhận redirect trình duyệt của khách hàng và xác thực kết quả thanh toán.
    - `POST /api/v1/payments/vnpay/reconcile` -> Kích hoạt batch đối soát định kỳ QueryDR thủ công (Role: `warehouse_staff`, `sales_staff`, `admin`).
  - Nhóm **Cart (Giỏ hàng & Biến thể - Sprint 2)**:
    - `GET /api/v1/cart` -> Lấy danh sách sản phẩm trong giỏ, tự động tính tổng tiền và gắn cờ `is_available` theo tồn kho thực tế.
    - `POST /api/v1/cart/items` -> Thêm/cộng dồn biến thể vào giỏ (Payload: `{"variant_id": "<UUID>", "quantity": 1}`).
    - `PATCH /api/v1/cart/items/{variant_id}` -> Cập nhật số lượng của một biến thể (Payload: `{"quantity": 2}`).
    - `DELETE /api/v1/cart/items/{variant_id}` -> Xóa 1 biến thể khỏi giỏ hàng (`204 No Content`).
    - `DELETE /api/v1/cart` -> Xóa sạch toàn bộ giỏ hàng của user sau khi đặt hàng (`204 No Content`).
  - Nhóm **Media & Cloud Storage**:
    - `POST /media/upload` -> Tải ảnh lên MinIO.
    - `GET /media/presigned-url` -> Lấy link xem ảnh riêng tư.
* **MinIO Web Console:** [http://localhost:9001](http://localhost:9001) (Tài khoản: `minioadmin` / `minioadmin`).
* **Kiểm tra Readiness:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)

### Bước 5: Chạy Bộ kiểm thử tự động (Unit Tests)
Bất kỳ thành viên nào sau khi kéo code hoặc sửa đổi đều có thể chạy toàn bộ test suite để đảm bảo không bị regression:
```powershell
docker exec virtufit_app_api python -m unittest discover -s tests -p "test_*.py"
```

### Bước 6: Khi muốn dừng hệ thống
```powershell
# Dừng container (Dữ liệu database, redis và ảnh minio vẫn được giữ nguyên)
docker compose down

# Nếu muốn xóa sạch toàn bộ dữ liệu database và ảnh để làm lại từ đầu:
docker compose down -v
```

> [!NOTE]
> **Cập nhật hạ tầng (25/10/2026):**
> 1. Đã chuyển đổi image MinIO sang `pgsty/silo:latest` và `pgsty/mc:latest` do MinIO đóng quyền truy cập anonymous trên Docker Hub và Quay.io. Image Silo tương thích 100% với S3 API và MinIO Web Console.
> 2. Đã bổ sung `greenlet>=3.0.0` phục vụ SQLAlchemy Async Engine.
> 3. Đã đồng bộ kiểu dữ liệu `datetime.utcnow()` cho PostgreSQL `TIMESTAMP WITHOUT TIME ZONE`.
> 4. Tất cả 4 services (`virtufit_postgres`, `virtufit_redis`, `virtufit_minio`, `virtufit_app_api`) đều đang chạy ở trạng thái `healthy`.
