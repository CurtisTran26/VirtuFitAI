# HƯỚNG DẪN HẠ TẦNG & NHẬT KÝ THAY ĐỔI (DEVOPS & BACKEND FOUNDATION)

> **Dự án:** VirtuFit AI — Hệ thống thương mại điện tử thời trang tùy chỉnh tích hợp AI  
> **Người thực hiện:** Đội ngũ Backend & DevOps  
> **Cập nhật lần cuối:** 16/10/2026  
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

---

## 🛠 Hướng dẫn cho thành viên nhóm khi kéo code về (Quickstart)

Mọi thành viên sau khi `git clone` hoặc `git pull` nhánh mới về, chỉ cần làm theo các bước sau:

### Bước 1: Chuẩn bị file môi trường
```powershell
# Sao chép từ mẫu biến môi trường
cp .env.example .env
```
*(Không chỉnh sửa file `.env.example`, chỉ chỉnh sửa file `.env` cá nhân nếu cần đổi mật khẩu hoặc cổng).*

### Bước 2: Khởi chạy môi trường với Docker
Yêu cầu: Đã bật **Docker Desktop**.
```powershell
# Build và chạy ngầm toàn bộ dịch vụ (Postgres, Redis, API)
docker compose up --build -d

# Xem log thời gian thực của backend
docker compose logs -f app-api
```

### Bước 3: Kiểm tra trạng thái hệ thống
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

### Bước 3: Nạp dữ liệu mẫu (Seed Data) — Chạy 1 lệnh duy nhất!
Sau khi container đã chạy, bạn chạy lệnh sau để tự động tạo bảng và nạp đầy đủ dữ liệu mẫu:
```powershell
# Cách 1 (Khuyên dùng - chạy trực tiếp trong container Docker):
docker compose exec app-api python -m backend.shared.database.seed

# Hoặc Cách 2 (nếu chạy từ môi trường Python máy host):
python -m backend.shared.database.seed
```
*(Lệnh này idempotent: chạy nhiều lần an toàn, không bị duplicate dữ liệu).*

### Bước 4: Kiểm tra kết nối từ trình duyệt / Postman
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
  - Nhóm **Media & Cloud Storage**:
    - `POST /media/upload` -> Tải ảnh lên MinIO.
    - `GET /media/presigned-url` -> Lấy link xem ảnh riêng tư.
* **MinIO Web Console:** [http://localhost:9001](http://localhost:9001) (Tài khoản: `minioadmin` / `minioadmin`).
* **Kiểm tra Readiness:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)

### Bước 5: Khi muốn dừng hệ thống
```powershell
# Dừng container (Dữ liệu database, redis và ảnh minio vẫn được giữ nguyên)
docker compose down

# Nếu muốn xóa sạch toàn bộ dữ liệu database và ảnh để làm lại từ đầu:
docker compose down -v
```

---

## 📋 Lộ trình các tính năng tiếp theo (Roadmap & Checklist)

File này sẽ được cập nhật sau mỗi lần hoàn thành các module dưới đây:

- [x] **Giai đoạn 1: Thiết lập Hạ tầng cơ sở (DevOps Foundation)**
- [x] **Giai đoạn 2: Cloud Object Storage & Phân quyền hình ảnh (MinIO/S3)**
- [x] **Giai đoạn 3: Database Models, Seed Data & API Catalog/Search/Filter**
- [x] **Giai đoạn 4: API Quét & Resolve Mã QR Sản phẩm tại cửa hàng (In-Store QR Scan)**
- [x] **Giai đoạn 5: API Hồ sơ người dùng & Số đo may mặc cho AI Try-On (Profile & Measurements)**
- [x] **Giai đoạn 6: Tích hợp Xác thực OTP Điện thoại & Đăng nhập không mật khẩu (Phone OTP & Passwordless Login)**
- [x] **Giai đoạn 7: Xác minh Google OAuth2 ID Token & Đăng nhập một chạm (Google Token Verification)**
- [ ] **Giai đoạn 8: Đăng ký tài khoản mật khẩu truyền thống & Đăng nhập username/password**
- [ ] **Giai đoạn 9: Giỏ hàng & Danh sách yêu thích (Cart & Wishlist)**
- [ ] **Giai đoạn 10: Đơn hàng & Thanh toán VNPay (Orders & Payments)**
- [ ] **Giai đoạn 11: Tích hợp Thử đồ AI & Tác vụ nền (AI Virtual Try-On Background Jobs)**
- [ ] **Giai đoạn 12: Cấu hình Backend thứ hai (`backend/management-api`)**






