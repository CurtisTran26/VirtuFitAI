# Chạy Web Admin và Warehouse

Hướng dẫn dành cho nhánh `frontend/loc-sprint1-web-updates`, chạy trên Windows bằng PowerShell.

## Cần cài

- Git
- Docker Desktop đang chạy
- Node.js LTS và npm
- Python 3.11 trở lên (chỉ cần nếu tạo tài khoản admin lần đầu bằng script)

## 1. Lấy code

Nếu chưa clone repo:

```powershell
git clone --single-branch --branch frontend/loc-sprint1-web-updates https://github.com/CurtisTran26/VirtuFitAI.git
cd VirtuFitAI
```

Nếu đã có repo, vào thư mục repo rồi chuyển nhánh:

```powershell
git switch frontend/loc-sprint1-web-updates
git pull
```

## 2. Khởi động database, storage và Management API

Chạy ở thư mục gốc repo:

```powershell
docker compose up -d --build postgres redis minio createbuckets management-api
```

Lần đầu Docker tải image và build API nên có thể mất vài phút. Kiểm tra API:

- Health: <http://localhost:8001/api/v1/health>
- Swagger: <http://localhost:8001/api/v1/docs>
- MinIO Console: <http://localhost:9001> (mặc định local: `minioadmin` / `minioadmin`)

## 3. Tạo schema cho database mới

Chỉ làm bước này khi vừa tạo database/volume mới, và chạy mỗi migration đúng một lần theo thứ tự. **Không chạy lại trên database nhóm đang có dữ liệu**; không xóa Docker volume để tránh mất dữ liệu.

Chạy từng lệnh từ thư mục gốc repo:

```powershell
Get-Content -Raw .\database\migrations\001_initial.sql | docker exec -i virtufit_postgres psql -v ON_ERROR_STOP=1 -U virtufit_user -d virtufit_db
Get-Content -Raw .\database\migrations\002_orders_returns.sql | docker exec -i virtufit_postgres psql -v ON_ERROR_STOP=1 -U virtufit_user -d virtufit_db
Get-Content -Raw .\database\migrations\003_catalog_options.sql | docker exec -i virtufit_postgres psql -v ON_ERROR_STOP=1 -U virtufit_user -d virtufit_db
Get-Content -Raw .\database\migrations\004_product_qr_codes.sql | docker exec -i virtufit_postgres psql -v ON_ERROR_STOP=1 -U virtufit_user -d virtufit_db
Get-Content -Raw .\database\seeds\001_roles.sql | docker exec -i virtufit_postgres psql -v ON_ERROR_STOP=1 -U virtufit_user -d virtufit_db
```

## 4. Tạo admin đầu tiên (database mới)

Việc này cần làm một lần vì seed chỉ tạo các role, không tạo tài khoản/mật khẩu mặc định. Mở PowerShell ở thư mục gốc repo:

```powershell
cd backend/management-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg://virtufit_user:virtufit_secure_password_dev@localhost:5432/virtufit_db"
$env:VIRTUFIT_ADMIN_PHONE = "SỐ_ĐIỆN_THOẠI_ADMIN"
$env:VIRTUFIT_ADMIN_NAME = "Tên admin"
$env:VIRTUFIT_ADMIN_PASSWORD = "Mật_khẩu_riêng_dài_tối_thiểu_16_ký_tự"
python ..\..\database\scripts\create_admin.py
Remove-Item Env:VIRTUFIT_ADMIN_PASSWORD
```

Tạo xong thì xóa các biến môi trường thông tin admin khỏi phiên PowerShell:

```powershell
Remove-Item Env:VIRTUFIT_ADMIN_PHONE, Env:VIRTUFIT_ADMIN_NAME, Env:DATABASE_URL
```

## 5. Chạy frontend Web

Mở terminal PowerShell thứ hai ở thư mục gốc repo:

```powershell
cd frontend/web
npm ci
Copy-Item .env.example .env
npm run dev
```

Mở địa chỉ Vite in trong terminal (thường là <http://localhost:5173>). Đăng nhập bằng số điện thoại và mật khẩu admin vừa tạo. Admin có thể tạo tài khoản nhân viên kho; đăng nhập bằng tài khoản kho sẽ vào trang Warehouse.

Frontend đọc URL API từ `frontend/web/.env`:

```env
VITE_MANAGEMENT_API_BASE_URL=http://localhost:8001/api/v1
```

## Dừng dịch vụ

Để dừng các container nhưng giữ dữ liệu:

```powershell
docker compose stop
```

Lần sau bật lại bằng `docker compose start`. Tránh `docker compose down -v`: tuỳ chọn `-v` xóa volume chứa database và storage.
