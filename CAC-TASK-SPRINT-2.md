# Kế hoạch & Tiêu chuẩn Nghiệm thu Backend - Sprint 2 (VirtuFit AI)

> **Lưu ý kiến trúc dự án:**
> - Hệ thống sử dụng **Khóa chính UUID** và mô hình biến thể **`product_variants`** (mỗi dòng đại diện cho một cặp `Size` + `Color`).
> - Tồn kho được quản lý kép qua hai cột: **`stock_on_hand`** (tồn kho thực tế) và **`reserved_quantity`** (số lượng đang giữ chỗ tạm thời khi khách đặt hàng nhưng chưa thanh toán).
> - Tiền tệ chuẩn hóa theo số nguyên **`price_vnd` / `total_vnd`**.
> - Mã đơn hàng định dạng chuẩn: **`order_number`** (ví dụ: `VF-20261029-ABCD`).
> - Tận dụng nền tảng nghiệp vụ đơn hàng & giữ kho đã được xây dựng sẵn trong **`backend/shared/order_service.py`**.

---

## 📌 [Đã có nền tảng - Giao thành viên khác] (BE) API Tạo đơn hàng và Giữ chỗ kho (Order Creation & Hold)
- **Codebase tham chiếu:** Đã có sẵn hàm `create_order()` trong `backend/shared/order_service.py` và router tại `backend/app-api/app/routers/orders/router.py`.
- **Nghiệp vụ:** 
  - Khóa chống trùng giao dịch bằng `Idempotency-Key` (dùng PostgreSQL advisory lock).
  - Snapshot thông tin sản phẩm tại thời điểm mua (`product_name_snapshot`, `sku_snapshot`, `size_snapshot`, `color_snapshot`, `unit_price_vnd`).
  - Tự động giữ chỗ tồn kho trong 15 phút: Tăng `product_variants.reserved_quantity` và tạo bản ghi `inventory_reservations` trạng thái `active`.
  - Thiết lập `hold_expires_at = now() + 15 phút`.

---

## 1. (BE) API Giỏ hàng và Validate biến thể (Cart & Variant Validation)

### Code
- **Cấu trúc dữ liệu Giỏ hàng:**
  - Mỗi mục giỏ hàng liên kết với: `user_id` (UUID), `variant_id` (UUID), và `quantity` (số lượng).
- **API `GET /api/v1/cart`:**
  - Lấy danh sách sản phẩm trong giỏ của người dùng hiện tại (Customer).
  - Tự động tính toán lại giá tiền thời gian thực từ bảng `products.price_vnd`.
  - Kiểm tra tính khả dụng: Gắn cờ `is_available = true/false` dựa trên:
    - Sản phẩm đang hoạt động: `products.is_active = true`.
    - Số lượng còn lại trong kho đủ đáp ứng: `(product_variants.stock_on_hand - product_variants.reserved_quantity) >= cart_item.quantity`.
  - Trả về payload tương thích 100% với Frontend Mobile:
    - `variant_id`, `product_id`, `product_name`, `color`, `size`, `price_vnd`, `quantity`, `line_total_vnd`, `image_url`.
- **API `POST /api/v1/cart/items`:**
  - Thêm một biến thể sản phẩm vào giỏ hàng (`variant_id`, `quantity`).
  - **Validate biến thể:** 
    - Kiểm tra `variant_id` tồn tại trong `product_variants`.
    - Kiểm tra sản phẩm cha `products.is_active = true`.
    - Kiểm tra số lượng yêu cầu `quantity <= (stock_on_hand - reserved_quantity)`.
  - **Cơ chế Upsert:** Nếu trong giỏ đã có `variant_id` này, tự động cộng dồn số lượng mới vào số lượng cũ (kiểm tra không vượt quá tổng tồn kho khả dụng).
- **API `PATCH /api/v1/cart/items/{variant_id}`:**
  - Cập nhật số lượng của một biến thể trong giỏ hàng.
  - Kiểm tra `quantity > 0` và không vượt quá tồn kho khả dụng.
- **API `DELETE /api/v1/cart/items/{variant_id}`:** Xóa một biến thể cụ thể khỏi giỏ hàng.
- **API `DELETE /api/v1/cart`:** Xóa sạch toàn bộ giỏ hàng của user sau khi đặt hàng thành công.

### Unit Test
- Test thêm biến thể hợp lệ vào giỏ hàng -> Trả về 201 Created.
- Test thêm biến thể đã có sẵn trong giỏ -> Số lượng được cộng dồn chính xác.
- Test thêm biến thể với số lượng vượt quá tồn kho khả dụng -> Báo lỗi 400 Bad Request / 409 Conflict.
- Test cập nhật số lượng biến thể `<= 0` -> Báo lỗi 422 Unprocessable Entity.
- Test sản phẩm cha bị ẩn (`is_active = false`) -> Báo lỗi không khả dụng khi lấy giỏ hàng.

---

## 2. (BE) VNPay Sandbox Integration (Create URL, IPN & Return)

### Code
- **Cấu hình:** Đọc từ file môi trường `.env`: `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_URL`, `VNPAY_RETURN_URL`.
- **API `POST /api/v1/payments/vnpay/create-url`:**
  - Nhận `order_id` (UUID).
  - Truy vấn đơn hàng: Kiểm tra `orders.status == 'pending_confirmation'` và `orders.payment_method == 'vnpay'`.
  - Kiểm tra thời hạn giữ chỗ: `orders.hold_expires_at > now()`.
  - Sinh URL thanh toán VNPay chuẩn version 2.1.0:
    - `vnp_TxnRef = order.order_number`
    - `vnp_Amount = order.total_vnd * 100` (VNPay nhân 100 lần)
    - `vnp_OrderInfo = "Thanh toan don hang {order_number}"`
    - Sắp xếp các tham số alphabet và sinh chữ ký HMAC-SHA512 (`vnp_SecureHash`).
- **API `GET /api/v1/payments/vnpay/ipn` (Webhook Server-to-Server):**
  - Tiếp nhận kết quả thanh toán ngầm từ máy chủ VNPay.
  - **Xác minh chữ ký:** Kiểm tra chữ ký hash từ tham số gửi về bằng `VNPAY_HASH_SECRET`. Sai -> Trả JSON: `{"RspCode": "97", "Message": "Invalid Checksum"}`.
  - **Truy vấn đơn hàng:** Tìm đơn hàng theo `order_number = vnp_TxnRef`. Không tìm thấy -> Trả JSON: `{"RspCode": "01", "Message": "Order Not Found"}`.
  - **Đối chiếu số tiền:** So sánh `vnp_Amount / 100 == order.total_vnd`. Sai -> Trả JSON: `{"RspCode": "04", "Message": "Invalid Amount"}`.
  - **Chống xử lý trùng lặp (Idempotent):**
    - Nếu `order.status == 'confirmed'` hoặc `order.payment_status == 'paid'` -> Trả ngay JSON: `{"RspCode": "02", "Message": "Order already confirmed"}` mà không xử lý lại.
  - **Cập nhật thanh toán thành công:**
    - Khi `vnp_ResponseCode == "00"`:
      - Gọi hàm `confirm_order(db, order_id, actor_id)` trong `order_service.py`:
        - Trừ tồn kho thực tế `stock_on_hand -= quantity`.
        - Trừ tồn kho giữ chỗ `reserved_quantity -= quantity`.
        - Đổi trạng thái đặt chỗ `inventory_reservations` sang `consumed`.
        - Ghi nhật ký vào `inventory_adjustments`.
        - Cập nhật `orders.status = 'confirmed'`, `orders.payment_status = 'paid'`.
      - Phản hồi: `{"RspCode": "00", "Message": "Confirm Success"}`.
- **API `GET /api/v1/payments/vnpay/return`:**
  - Nhận redirect từ trình duyệt của khách sau khi thanh toán.
  - Xác thực chữ ký và chuyển hướng hoặc trả kết quả tóm tắt cho Frontend Mobile/Web.

### Unit Test
- Test sinh URL thanh toán VNPay có đầy đủ tham số và chữ ký HMAC-SHA512 chuẩn.
- Test IPN thành công (`vnp_ResponseCode = "00"`) -> Đơn đổi sang `confirmed`, kho thực tế được khấu trừ.
- Test IPN sai chữ ký (`vnp_SecureHash` giả) -> Trả về `RspCode: "97"`.
- Test IPN sai lệch số tiền -> Trả về `RspCode: "04"`.
- Test gọi IPN 2 lần liên tiếp cho cùng 1 đơn -> Lần 2 trả `RspCode: "02"` và không trừ kho 2 lần.

---

## 3. (BE) API Thanh toán tại quầy (Counter Order: Cash & VietQR)

### Code
- **Phân quyền bảo mật:** Chỉ tài khoản có vai trò `sales_staff` hoặc `admin` mới được quyền gọi.
- **Tạo đơn tại quầy:** Hỗ trợ đơn bán hàng trực tiếp với `order_type = 'counter'`, `customer_id = None` (khách vãng lai).
- **API `POST /api/v1/sales/orders/{order_id}/pay-cash` (Thanh toán tiền mặt):**
  - Nhận: `cash_received` (số tiền khách đưa).
  - Validate: `cash_received >= order.total_vnd`. Báo lỗi 400 nếu khách đưa thiếu tiền.
  - Tính tiền thừa: `cash_change = cash_received - order.total_vnd`.
  - Khấu trừ tồn kho ngay lập tức và hoàn tất đơn hàng:
    - Cập nhật `orders.status = 'completed'`, `orders.payment_status = 'paid'`, `orders.payment_method = 'cash'`.
    - Lưu snapshot thông tin giao dịch vào trường ghi chú / lịch sử đơn: `cash_received`, `cash_change`, `staff_id`.
- **API `POST /api/v1/sales/orders/{order_id}/vietqr` (Sinh mã QR chuyển khoản tại quầy):**
  - Sinh payload chuẩn VietQR (theo chuẩn Napas 247):
    - Mã ngân hàng (`bank_id`), Số tài khoản thụ hưởng (`account_no`), Tên chủ tài khoản (`account_name`).
    - Số tiền: `order.total_vnd`.
    - Nội dung chuyển khoản: `{order_number}`.
  - Trả về chuỗi EMVCo payload hoặc URL ảnh QR từ cổng VietQR (để nhân viên quầy đưa khách quét mã).
- **API `POST /api/v1/sales/orders/{order_id}/confirm-transfer`:**
  - Nhân viên xác nhận tiền đã về tài khoản ngân hàng -> Hoàn tất đơn sang `completed`, `payment_status = 'paid'`.

### Unit Test
- Test nhân viên sales thanh toán tiền mặt đủ -> Đơn chuyển `completed`, trả về tiền thừa chính xác.
- Test khách đưa thiếu tiền mặt -> Báo lỗi 400 Bad Request.
- Test sinh payload VietQR khớp chính xác mã đơn và số tiền cần thanh toán.
- Test tài khoản vai trò `customer` cố tình gọi API thanh toán quầy -> Chặn 403 Forbidden.

---

## 4. (BE) API Đơn hàng COD và Xác nhận Thu tiền (Cash on Delivery)

### Code
- **Điều kiện đặt đơn COD:**
  - Khi tạo đơn qua `POST /orders`, nếu `payment_method = 'cod'`:
    - Bắt buộc kiểm tra `address_snapshot` phải có đầy đủ: địa chỉ chi tiết, người nhận, số điện thoại người nhận.
    - Đơn tạo thành công với `orders.status = 'confirmed'` (đã duyệt đơn giao) và `orders.payment_status = 'unpaid'`.
- **API `POST /api/v1/orders/{order_id}/cod-collect` (Xác nhận đối soát tiền COD):**
  - Phân quyền: Dành cho `warehouse_staff`, `sales_staff` hoặc `admin`.
  - **Kiểm tra trạng thái hợp lệ:**
    - Đơn hàng bắt buộc phải ở trạng thái `shipped` (đang giao) hoặc `completed` (đã giao thành công).
    - Nếu đơn còn đang ở `pending_confirmation` hoặc `processing` -> Từ chối báo lỗi 400.
  - **Chống thu trùng:**
    - Kiểm tra `orders.payment_status == 'unpaid'`. Nếu đã là `'paid'` -> Báo lỗi 409 Conflict.
  - **Cập nhật:**
    - Đổi `orders.payment_status = 'paid'`.
    - Ghi nhận nhân viên xác nhận và thời gian đối soát vào `order_status_history`.

### Unit Test
- Test tạo đơn hàng COD hợp lệ -> Trạng thái ban đầu: `payment_status = 'unpaid'`.
- Test xác nhận thu COD khi đơn hàng mới đang đóng gói (`processing`) -> Báo lỗi 400.
- Test xác nhận thu COD khi đơn đã giao (`completed`) -> Cập nhật thành công sang `paid`.
- Test cố tình xác nhận thu COD lần thứ 2 cho cùng 1 đơn -> Báo lỗi 409 Conflict.

---

## 5. (BE) API Xử lý Đóng gói & Giao nhận (Fulfillment State Machine)

### Code
- **Cơ sở hạ tầng:** Tích hợp trực tiếp hàm `update_order_status()` trong `backend/shared/order_service.py`.
- **Phân quyền:** Dành riêng cho `warehouse_staff` và `admin`.
- **API `GET /api/v1/warehouse/orders`:**
  - Lấy danh sách các đơn hàng cần chuẩn bị đóng gói (`status = 'confirmed'`).
  - Lọc theo ngày đặt, phương thức giao hàng (`online` hoặc `counter`).
- **API `PATCH /api/v1/warehouse/orders/{order_id}/status`:**
  - Thực thi quy trình chuyển trạng thái nghiêm ngặt (Fulfillment State Machine):
    - **Bước 1 (Bắt đầu soạn hàng):** `confirmed` -> `processing`
    - **Bước 2 (Đóng gói xong, chờ ship):** `processing` -> `ready_to_ship`
    - **Bước 3 (Bàn giao vận chuyển):** `ready_to_ship` -> `shipped`
      - **Validate nghiệp vụ bắt buộc:** Khi chuyển sang `shipped`, payload **bắt buộc** phải có `carrier_name` (đơn vị vận chuyển: GHN, GHTK, ViettelPost) và `tracking_code` (mã vận đơn).
    - **Bước 4 (Giao thành công):** `shipped` -> `completed`
  - Tự động ghi vết vào bảng `order_status_history` gồm: `from_status`, `to_status`, `changed_by`, `note`.

### Unit Test
- Test lấy danh sách đơn cần soạn hàng cho nhân viên kho.
- Test chuyển tuần tự trạng thái đơn hàng: `confirmed` -> `processing` -> `ready_to_ship` -> `shipped`.
- Test nhảy cóc trạng thái (từ `confirmed` nhảy thẳng lên `completed`) -> Báo lỗi 409 State Conflict.
- Test chuyển sang `shipped` nhưng không truyền mã vận đơn `tracking_code` -> Báo lỗi 422 Unprocessable Entity.
- Test tài khoản `customer` hoặc `designer` cố gọi API chuyển trạng thái kho -> Chặn 403 Forbidden.

---

## 6. (BE) Đối soát Giao dịch Định kỳ & QueryDR VNPay (Reconciliation Worker)

### Code
- **Cơ chế chạy nền (Background Worker):** 
  - Khởi tạo tiến trình quét định kỳ (mỗi 5 - 10 phút) sử dụng `APScheduler` (tích hợp trong FastAPI startup) hoặc worker daemon.
- **Tiêu chí quét đơn hàng:**
  - Tìm các đơn hàng thỏa mãn:
    - `payment_method = 'vnpay'`
    - `status = 'pending_confirmation'`
    - `payment_status = 'unpaid'`
    - Thời gian tạo đã trôi qua quá 10 phút (khách đã có thời gian thực hiện thanh toán trên cổng VNPay).
- **Khóa chống đụng độ (Concurrency Control):**
  - Sử dụng PostgreSQL transaction lock `FOR UPDATE SKIP LOCKED` hoặc Redis lock theo `order_number` để ngăn worker chạy đè lên webhook IPN của VNPay.
- **Tích hợp API truy vấn kết quả VNPay (QueryDR):**
  - Gửi request truy vấn giao dịch tới VNPay (`vnp_Command = "querydr"`).
  - Nếu kết quả trả về từ ngân hàng là **Đã thanh toán thành công (`vnp_ResponseCode == "00"` và `vnp_TransactionStatus == "00"`)**:
    - Tự động gọi `confirm_order()`: Trừ kho thực tế, đổi `status = 'confirmed'`, `payment_status = 'paid'`.
    - Ghi log đối soát tự động: *"Reconciliation worker: Confirmed order via QueryDR"*.
  - Cơ chế Exponential Backoff: Thử lại tối đa 3 chu kỳ trước khi dừng truy vấn.

### Unit Test
- Test worker quét đúng các đơn VNPay treo quá 10 phút.
- Test cơ chế khóa chống xung đột giữa QueryDR worker và Webhook IPN.
- Test mock API VNPay QueryDR trả về `00` -> Đơn hàng được tự động xác nhận và khấu trừ kho.
- Test đơn hàng đã thanh toán không bị worker quét lại.

---

## 7. (BE) API Hoàn tiền & Hoàn trả Tồn kho (Refund & Restock)

### Code
- **Cơ sở hạ tầng:** Tích hợp hàm `cancel_order(..., allow_confirmed=True)` trong `backend/shared/order_service.py`.
- **Phân quyền:** Chỉ tài khoản có vai trò `admin` (hoặc `sales_manager`) được phép thực hiện hoàn tiền.
- **API `POST /api/v1/admin/orders/{order_id}/refund`:**
  - **Validate điều kiện hoàn tiền:**
    - Đơn hàng bắt buộc phải ở trạng thái đã thanh toán: `orders.payment_status == 'paid'`.
    - Đơn chưa từng bị hoàn tiền trước đó (`orders.payment_status != 'refunded'`).
  - **Cập nhật trạng thái đơn:**
    - Đổi `orders.payment_status = 'refunded'`.
    - Đổi `orders.status = 'cancelled'`.
  - **Nghiệp vụ Hoàn trả tồn kho (Restock Logic):**
    - Tự động hoàn trả số lượng của từng món trong `order_items` về lại cột `stock_on_hand` của bảng `product_variants`.
    - Tạo bản ghi điều chỉnh kho trong `inventory_adjustments` với:
      - `delta = +quantity`
      - `reason = "Order {order_number} refunded & restocked by Admin"`.
  - Ghi nhận thông tin hoàn tiền: `refund_amount`, `refund_reason`, `admin_id`.

### Unit Test
- Test Admin hoàn tiền hợp lệ -> `payment_status` chuyển thành `refunded`, `status` chuyển thành `cancelled`.
- **Test Restock kho:** Kiểm tra `product_variants.stock_on_hand` tăng lại chính xác bằng số lượng của các món trong đơn hoàn.
- Test hoàn tiền cho đơn chưa thanh toán (`payment_status = 'unpaid'`) -> Báo lỗi 400 Bad Request.
- Test cố tình gọi hoàn tiền lần thứ 2 cho đơn đã hoàn tiền -> Báo lỗi 409 Conflict.

---

## 8. (BE) Job Tự động Hủy Đơn Quá hạn Giữ chỗ (Auto-Cancel Expired Orders)

### Code
- **Cơ sở hạ tầng:** Kích hoạt hàm `expire_stale_holds(db)` đã có sẵn trong `backend/shared/order_service.py`.
- **Cơ chế chạy nền (Background Cron Job):**
  - Thiết lập chạy định kỳ **mỗi 5 phút một lần**.
- **Điều kiện phát hiện đơn quá hạn:**
  - `orders.status == 'pending_confirmation'`
  - `orders.hold_expires_at <= now()` (đã hết 15 phút giữ chỗ kho tạm thời mà khách không thanh toán VNPay).
- **Quy trình hủy đơn & Thu hồi giữ chỗ kho tự động:**
  - Chuyển `orders.status = 'expired'`.
  - Xóa thời gian giữ chỗ: `orders.hold_expires_at = NULL`.
  - **Giải phóng giữ chỗ kho (Release Reservation):**
    - Trừ ngược `product_variants.reserved_quantity -= reservation.quantity` (giúp số tồn kho này quay trở lại làm tồn kho khả dụng để khách khác có thể đặt mua).
    - Cập nhật trạng thái trong bảng `inventory_reservations` từ `'active'` sang `'released'`.
  - Ghi lịch sử đơn vào `order_status_history`: `note = "Inventory hold expired after 15 minutes"`.

### Unit Test
- Test đơn hàng VNPay quá hạn 15 phút -> Tự động chuyển sang trạng thái `expired`.
- **Test giải phóng tồn kho:** Kiểm tra `product_variants.reserved_quantity` giảm về mức ban đầu, tồn kho khả dụng tăng trở lại cho người khác mua.
- Test đơn hàng đã thanh toán (`status = 'confirmed'`) hoặc đơn COD không bị hủy nhầm.


---

## 9. S2-035: (BE) PoC AI Thử Đồ Ảo với Fashn.ai (Virtual Try-On - VTON)

### Code & Kiến trúc
- **Tầng tích hợp Adapter (`backend/app-api/app/integrations/ai_service/try_on/`):**
  - `base.py`: Interface `BaseTryOnProvider` định nghĩa phương thức trừu tượng `submit_try_on(...)` và `get_try_on_status(...)`.
  - `fashn_provider.py`: Tích hợp chính thức với **Fashn.ai API** (`https://api.fashn.ai/v1/run`).
    - Nhận dữ liệu: `model_image` (URL ảnh người dùng từ `virtufit-private`), `garment_image` (URL ảnh sản phẩm từ `virtufit-public`), `category` (`tops`, `bottoms`, `one-pieces`).
    - Quản lý API Key bảo mật qua biến môi trường: `FASHN_API_KEY`.
  - `mock_provider.py`: Giả lập phản hồi thành công từ kho ảnh mẫu nội bộ MinIO trong 0.2s để chạy Unit Test và phát triển độc lập không phụ thuộc mạng/hết quota.
- **Service & Quản lý tác vụ bất đồng bộ:**
  - Khởi tạo tác vụ thử đồ và trả về `task_id` cho Mobile (tránh chặn HTTP request lâu).
  - Khi hoàn thành: Tự động tải ảnh kết quả về lưu bền vững vào MinIO bucket `virtufit-private/try-on/{user_id}/{task_id}.png`.
  - Sinh Presigned URL an toàn (hạn dùng 30 phút) để Mobile hiển thị ảnh cho khách hàng.
- **API Endpoints:**
  - `POST /api/v1/try-on/submit`: Tiếp nhận yêu cầu thử đồ (User, Product, Category).
  - `GET /api/v1/try-on/tasks/{task_id}`: Kiểm tra tiến độ và nhận kết quả thử đồ.

### Unit Test (`tests/unit/test_ai_try_on.py`)
- Test kiểm tra tính hợp lệ của dữ liệu đầu vào (định dạng ảnh, dung lượng ≤ 5MB, product tồn tại).
- Test luồng xử lý Mock Provider thành công: Sinh `task_id`, trả kết quả và lưu đúng bucket MinIO `virtufit-private`.
- Test xử lý lỗi khi Fashn.ai trả về lỗi (401 sai API Key, 429 quá tải, ảnh khuôn mặt bị che khuất) -> Backend bắt lỗi an toàn và trả mã lỗi chuẩn `502 Bad Gateway`.

---

## 10. S2-036: (BE) PoC AI Tạo Concept Thiết Kế Riêng với FLUX.1 (Fashion Concept Generation)

### Code & Kiến trúc
- **Tầng tích hợp Adapter (`backend/app-api/app/integrations/ai_service/concept/`):**
  - `base.py`: Interface `BaseConceptProvider` định nghĩa `generate_concepts(...)`.
  - `flux_provider.py`: Tích hợp mô hình **FLUX.1 (bản flux-schnell / flux-dev)** qua Replicate/Fal.ai API.
    - Quản lý cấu hình qua `.env`: `FLUX_API_KEY`, `FLUX_MODEL_VERSION`.
    - Sinh từ 1 đến 4 biến thể concept phác thảo theo yêu cầu.
  - `mock_provider.py`: Trả về danh sách concept giả lập từ ảnh mẫu lưu sẵn trong MinIO để phục vụ test tự động và ghép màn hình Mobile.
- **Bộ chuẩn hóa Prompt thời trang (Fashion Prompt Enrichment):**
  - Tự động bổ sung các từ khóa chuyên ngành vào mô tả của khách:
    `"Professional fashion lookbook studio shot, detailed fabric texture of {material}, {style_preset} aesthetic, high-end tailoring, clean neutral backdrop, realistic lighting"`
- **Lưu trữ & Xuất bản:**
  - Lưu ảnh các concept vào MinIO `virtufit-private/custom-designs/concepts/{concept_id}.png`.
  - Tạo Presigned URL cho khách hàng duyệt mẫu trên Mobile và Designer thẩm định báo giá.
- **API Endpoint:**
  - `POST /api/v1/custom-design/concepts/generate`: Tiếp nhận prompt ý tưởng, phong cách, giới tính, số lượng ảnh cần sinh.

### Báo cáo So sánh & Đánh giá PoC (`AI_POC_BENCHMARK_REPORT.md`)
- Đo lường và tổng kết số liệu thực tế:
  - Thời gian xử lý trung bình của FLUX.1-schnell (mục tiêu: ≤ 4 giây).
  - Chi phí thực tế mỗi concept (mục tiêu: ≤ 0.03 USD / ảnh).
  - Đánh giá khả năng bám sát prompt tiếng Việt và tính khả thi may mẫu thực tế.

### Unit Test (`tests/unit/test_ai_concept.py`)
- Test kiểm tra validation prompt: Độ dài (10 - 1000 ký tự), lọc từ khóa cấm/nhạy cảm.
- Test bộ làm giàu prompt (Prompt Builder) tự động gắn style và tham số kỹ thuật may mặc.
- Test Mock Concept Provider sinh thành công danh sách biến thể ảnh và lưu vào MinIO.
- Test xử lý ngoại lệ khi API AI bị timeout hoặc hết credit.
