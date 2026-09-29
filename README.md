# VirtuFit AI — cấu trúc đầy đủ

Chỉ có thư mục và tài liệu hướng dẫn. Chưa có code, package.json hoặc server để chạy.
Tên thư mục chức năng là nhóm công việc, không phải microservice riêng. Có thể gộp file khi triển khai để code đơn giản.

## Phạm vi
- frontend/mobile: app Customer và Sales Staff.
- frontend/web: web Admin, Warehouse Staff và Designer; thanh điều hướng ngang phía trên.
- backend/app-api: backend riêng cho app.
- backend/management-api: backend riêng cho web.
- backend/shared: model, xác thực, phân quyền và quy tắc nghiệp vụ dùng chung; không phải server thứ ba.
- database: một PostgreSQL chung; chỉ một bộ migrations ở đây.
- ai: tích hợp thử đồ và sinh ý tưởng thiết kế; không yêu cầu tự huấn luyện model.
- infra: cấu hình môi trường và triển khai.
- docs: tài liệu, backlog, sprint, kiểm thử và bảo vệ.
- tests: Postman, kiểm thử tích hợp và luồng toàn hệ thống.

## Quy tắc nghiệp vụ
- Xác minh OTP qua điện thoại; Google login sử dụng tài khoản Google, không có email OTP.
- Địa chỉ nhận hàng nhập tại checkout, không tạo chức năng quản lý sổ địa chỉ riêng.
- QR sản phẩm khác QR chuyển khoản.
- Customer gửi brief → AI tạo concept → Designer kiểm tra/chỉnh sửa/báo giá → Customer duyệt → Sales Staff tạo đơn custom → Customer xác nhận/thanh toán → Warehouse nhận xử lý.
- Các trao đổi qua hệ thống; chat và thông báo dùng chung, không nối trực tiếp actor với nhau.
- Báo cáo doanh thu thuộc Admin. Kho cập nhật tồn và tình trạng xử lý đơn. Designer cập nhật thông tin tiến độ thiết kế/sản xuất theo phạm vi được giao.
- Chat hỗ trợ nhân viên và phản hồi chatbot đặt trong nhóm chat; AI try-on và AI design-generation tách rõ.

## Cách dùng
Mở thư mục này bằng VS Code. Thành viên viết code vào phần phụ trách, không cần tạo code cho mọi thư mục ngay lập tức.
Frontend services/api gọi backend; backend routers nhận request, schemas định nghĩa dữ liệu, services xử lý nghiệp vụ.
Backend tests dành cho unit/integration của API; tests ở gốc dành cho kiểm thử xuyên hệ thống. Trình phụ trách tài liệu và manual test; lập trình viên phụ trách automated test.
.gitkeep chỉ giữ thư mục trống trên GitHub.
Xem STRUCTURE.md để xem toàn bộ cây thư mục.

## Phân công
- Duy: frontend/mobile.
- Lộc: frontend/web, phối hợp màn app theo task.
- Giáp: backend/app-api.
- An: backend/management-api; phối hợp AI với Giáp.
- Trinh: docs, test cases, manual test, bug và retest.
- Giáp và An cùng thống nhất database, shared và API contract.


# HƯỚNG DẪN CHUNG TRƯỚC KHI CODE

Cập nhật: 29/09/2026. Đây là đầu mối thống nhất của nhóm. Quyết định mới phải được cập nhật vào README qua PR; không chỉ thông báo trong tin nhắn.
**Trạng thái hiện tại: chỉ là cấu trúc thư mục. Clone được nhưng chưa chạy được.** Không có API, UI, database hoặc dịch vụ ngoài đã triển khai. Tài liệu mô tả kế hoạch, không phải tính năng đã hoàn thành.

## 1. Đọc gì trước khi làm task?
1. README này: phạm vi, kiến trúc, quy trình và các điểm ★ cần chốt.
2. [STRUCTURE.md](STRUCTURE.md): vị trí từng thư mục.
3. Task và acceptance criteria trong bảng sprint được nhóm duyệt.
4. Ảnh thiết kế mới nhất ứng với màn hình được giao.
5. API contract của chức năng trước khi nối frontend–backend.

README thay bản thống nhất riêng; không thay thế ảnh thiết kế, bảng giao việc, schema chi tiết hoặc test case. Các thư mục docs hiện trống: chưa có các tài liệu này trong ZIP. Nhóm phải đưa bản đang dùng vào đúng chỗ trước khi triển khai task liên quan.

| Nội dung | Chỗ đặt |
|---|---|
| Product Backlog | docs/product-backlog/ |
| Bảng Sprint 1–4 | docs/sprint-backlogs/sprint-1/ … sprint-4/ |
| Thiết kế app/web | docs/ui-design/mobile/ và docs/ui-design/web/ |
| API app/web | docs/api-contracts/app-api/ và management-api/ |
| ERD, data dictionary | docs/database-design/ |
| Test case, lỗi, báo cáo | docs/test-cases/, bug-reports/, test-reports/ |



## 2. Công nghệ và môi trường
| Phần | Thống nhất |
|---|---|
| App | React Native + Expo; JavaScript, React Native StyleSheet; mục tiêu Android |
| Web | React + Vite; JavaScript/JSX và CSS thuần |
| Backend | Hai ứng dụng Python FastAPI độc lập |
| Database | PostgreSQL dùng chung |
| File ảnh | Object storage; PostgreSQL lưu tham chiếu và metadata |
| AI | Tích hợp model pretrained hoặc API; thử đồ và sinh concept là hai tác vụ |
| Công cụ | VS Code, Git/GitHub, Postman; Android Studio/thiết bị Android; Docker cho môi trường |

Không cần đổi sang TypeScript/Tailwind hoặc thêm framework mới nếu chưa có lý do được nhóm thống nhất. React web sử dụng JSX gần cú pháp HTML; React Native sử dụng View/Text, không dùng thẻ HTML. Ưu tiên hàm ngắn, tên rõ nghĩa và code có thể giải thích khi bảo vệ.

★ Phiên bản Node, Python, Expo, React Native, React, FastAPI phải được người khởi tạo ghi chính xác sau khi thử chạy. Không cài từng thư viện lên bản mới nhất riêng lẻ. Expo và React Native phải tương thích; Expo Go khác SDK có thể không chạy. Khung thư mục này chưa chốt phiên bản/lockfile.

## 3. Khởi tạo nền tảng — làm một lần trước khi code nghiệp vụ
| Chủ trì | Việc cần làm | Điều kiện hoàn thành |
|---|---|---|
| Duy | Khởi tạo Expo trong frontend/mobile, giữ các thư mục chức năng; tạo navigation, màn khởi đầu | Chạy được trên Android; commit cấu hình và lockfile |
| Lộc | Khởi tạo React/Vite trong frontend/web; routing, layout ngang và CSS chung | Chạy dev và build được; commit lockfile |
| Giáp | Khởi tạo App API, health, cấu hình và xử lý lỗi chung | API 8000 trả health, có request/response mẫu |
| An | Khởi tạo Management API, health và CORS | API 8001 trả health; web gọi được |
| Giáp + An | Cài shared như package Python, thống nhất schema/migration/database | Hai API dùng cùng schema; migration chỉ ở database/migrations |
| Trình | Kiểm tra hướng dẫn cài trên máy khác, test case môi trường | Ghi kết quả, lỗi và bước tái hiện |

Chốt scripts frontend: app `npm start`, web `npm run dev`/`npm run build`. Chốt entrypoint backend `app.main:app` và requirements.txt cho từng API. Sau khi khởi tạo mới áp dụng các lệnh ở mục 4. Chưa khởi tạo thì npm ci và uvicorn sẽ thất bại.

## 4. Clone và chạy sau khi khung chạy được đã merge
```powershell
git clone https://github.com/YOUR_USERNAME/virtufit-ai.git
cd virtufit-ai
code .
```
Thay URL bằng repository thật. Đường dẫn Windows nên là D:\VirtuFitAI, tránh ký tự &. Không copy node_modules hoặc .venv của người khác.

Frontend (terminal ở frontend/web hoặc frontend/mobile):
```powershell
npm ci
Copy-Item .env.example .env
# Sửa giá trị .env theo máy của mình.
# Web: npm run dev
# App: npm start
```
Mỗi backend dùng terminal và .venv riêng (ví dụ App API):
```powershell
cd backend/app-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Management API tương tự, cổng 8001. Cách load .env phải được người khởi tạo triển khai và ghi lại; không mặc định uvicorn tự đọc .env.

| Biến cấu hình dự kiến | Nơi dùng |
|---|---|
| EXPO_PUBLIC_API_BASE_URL=http://IP_MAY_TINH:8000/api/v1 | App |
| VITE_API_BASE_URL=http://localhost:8001/api/v1 | Web |
| DATABASE_URL | Cả hai backend, cùng database |
| CORS_ORIGINS | Backend, danh sách origin web được phép |
| JWT / OTP / Google / VNPay / AI / storage credentials | Backend, chỉ thêm khi chọn tích hợp |

Frontend chỉ chứa URL và cấu hình công khai, không chứa secret. Điện thoại dùng IP LAN máy chạy API, không dùng localhost. Máy và điện thoại cùng mạng; kiểm tra firewall khi không kết nối. Các file .env.example phải dùng giá trị mẫu, không có credential thật.

## 5. Quyền của từng vai trò
| Vai trò | Quyền chính |
|---|---|
| Customer | Đăng ký; mua hàng; QR; thử đồ; thiết kế riêng; xem dữ liệu cá nhân |
| Sales Staff | Tra cứu sản phẩm/tồn; kiểm tra đơn; tạo đơn quầy/custom; ghi nhận thanh toán; hỗ trợ khách |
| Warehouse Staff | Sản phẩm/danh mục/size/ảnh; tồn kho; QR; nhận và xử lý đơn; đóng gói/cập nhật giao hàng |
| Designer | Nhận brief/concept; đánh giá khả thi; chỉnh thiết kế; báo giá; theo dõi phản hồi/tiến độ |
| Admin | Tài khoản, phân quyền, doanh thu, thống kê tương tác |

Chỉ Customer tự đăng ký. Admin cấp tài khoản nhân viên/Designer. Backend kiểm tra role và quyền sở hữu dữ liệu cho mọi API bảo vệ. Ẩn nút hoặc chặn trang frontend không thay thế phân quyền backend. Không cho client gửi role tùy ý để tự nâng quyền.

## 6. Các luồng phải thống nhất
### Xác thực
Điện thoại + mật khẩu, xác minh bằng OTP điện thoại. Google login: app nhận token Google, backend xác minh rồi tạo phiên. Không tin email/role do frontend tự gửi. OTP có hạn dùng, giới hạn thử/gửi lại và chỉ dùng một lần. Logout phải vô hiệu phiên theo thiết kế backend. Không tự liên kết hai tài khoản chỉ vì email trùng.

### Mua hàng thông thường
Xem/tìm/quét QR → chi tiết → màu/size/số lượng → giỏ → checkout và địa chỉ → chọn COD/VNPay → tạo đơn → theo dõi. Khách ở nhà có thể chọn sản phẩm và thử đồ mà không quét QR.
Backend tính giá/tổng tiền/tồn kho, lưu snapshot giá và địa chỉ đơn; không tin tổng tiền frontend gửi lên.

### Bán tại quầy
Nhân viên tra/tạo đơn → kiểm tra sản phẩm, size, lượng, giá → xác nhận khách chọn tiền mặt/chuyển khoản → thu tiền → xác nhận kết quả → biên nhận.
Tiền mặt kiểm tra tiền nhận đủ và tính tiền thừa. QR chuyển khoản chỉ cung cấp thông tin chuyển tiền, không chứng minh đã trả. Chưa tích hợp đối soát ngân hàng thì ghi nhận bằng thao tác nhân viên có nhật ký.

### Thử đồ AI
Chọn sản phẩm → chụp/tải ảnh → kiểm tra ảnh → tạo tác vụ → chờ xử lý → kết quả hoặc lỗi/thử lại → lưu/xóa kết quả theo quyền.
Không hiển thị ảnh demo như kết quả AI thật. Gợi ý size cơ bản dùng chiều cao/cân nặng và bảng size sản phẩm, không tuyên bố đo cơ thể chính xác từ ảnh.

### Thiết kế riêng
Customer gửi yêu cầu/ảnh tham khảo → hệ thống gọi AI tạo concept → Designer đánh giá khả thi, yêu cầu bổ sung/chỉnh sửa và báo giá → Customer duyệt → hệ thống chuyển hồ sơ cho Sales Staff → Sales Staff tạo đơn → Customer xác nhận/thanh toán → Warehouse nhận yêu cầu xử lý → cập nhật tiến độ qua hệ thống.
Designer không tự quyết thay Customer việc duyệt mẫu. AI tạo concept không đảm bảo bản rập may hoặc khả năng sản xuất. ★ Nhóm phải chốt ai thực sự sản xuất trang phục và ai cập nhật từng mốc; Warehouse không mặc nhiên là thợ may.

### Chat, thông báo, báo cáo
Trao đổi Customer–Sales/Designer qua hệ thống; phân biệt chatbot tự động và nhân viên thật. Chatbot không tự thay đổi giá, đơn hoặc quyết định hoàn tiền. Thông báo đưa người dùng về hồ sơ/đơn liên quan. Admin xem số liệu từ dữ liệu thật, không đưa số demo vào báo cáo thật.

## 7. API contract — phải thống nhất trước khi nối giao diện
Quy ước cho khung này: prefix `/api/v1`, JSON snake_case, ID UUID dạng chuỗi, tiền VND số nguyên, ngày giờ ISO8601 UTC. Hiển thị giờ Việt Nam tại frontend. Danh sách dùng page/limit; đề xuất giới hạn limit tối đa 100.

Mỗi endpoint cần: method/path, backend sở hữu, role được dùng, request, response thành công, lỗi, ví dụ và rule nghiệp vụ. Frontend có thể mock theo contract, nhưng ghi rõ mock và phải thay bằng API thật khi nghiệm thu tích hợp.
Ví dụ lỗi thống nhất:
```json
{"error":{"code":"OUT_OF_STOCK","message":"Sản phẩm không đủ tồn kho","details":{}}}
```
400/422: dữ liệu không hợp lệ; 401: chưa xác thực; 403: thiếu quyền; 404: không tìm thấy; 409: xung đột trạng thái/tồn kho; 500: lỗi hệ thống, không trả stacktrace/secret cho người dùng.

Hai API không được tự định nghĩa hai bộ trạng thái/size/model khác nhau. Auth dùng chung cơ chế xác minh trong shared, nhưng mỗi API vẫn kiểm tra role. Chỉ App API xử lý callback VNPay của đơn thanh toán trong app; báo cáo web đọc kết quả chung. Callback phải kiểm chữ ký, mã đơn, số tiền và chống xử lý lặp; trang trình duyệt báo thành công chưa đủ để xác nhận thanh toán.

## 8. Dữ liệu, trạng thái và chống xử lý trùng
- Một nơi quản lý migration: database/migrations. Không sửa database riêng lẻ rồi quên migration.
- Shared chứa quy tắc dùng chung cho đơn, tồn, thanh toán; hai API không chép hai bản logic.
- Cập nhật đơn/tồn bằng transaction; kiểm tra tranh chấp khi hai người cùng mua. Chống tạo/thu tiền/trừ kho hai lần khi retry hoặc callback lặp.
- Tách trạng thái đơn, thanh toán và yêu cầu thiết kế. Bảng chuyển trạng thái phải được Giáp/An chốt trong docs trước khi code.
- Ví dụ trạng thái để nhóm hoàn thiện: đơn pending/confirmed/packing/shipped/delivered/cancelled; thanh toán unpaid/pending/paid/failed/refunded; thiết kế submitted/reviewing/revision_requested/quoted/approved/rejected.
- Các trạng thái trên là đề xuất, chưa phải schema đã duyệt. Không dùng chúng thay cho thiết kế xử lý trả hàng/hoàn tiền chi tiết.
- Không xóa cứng sản phẩm có đơn lịch sử; cân nhắc inactive/soft-delete. Tồn quản lý theo biến thể màu và size.
- Ảnh người dùng cần quyền truy cập; không commit ảnh thật, không log token/OTP/password. ★ Chốt thời hạn lưu/xóa ảnh và ngân sách cloud.

## 9. Quy ước frontend và cách viết code
- Tham khảo đúng ảnh mới nhất; ảnh cũ chỉ dùng cho màn chưa thay thế. Giá, tên, size theo tài liệu/dữ liệu chung.
- Web giữ navigation ngang phía trên; không đổi sang sidebar.
- Màn hình trong screens/pages; thành phần lặp lại trong components; gọi API qua services/api; không rải URL trong từng màn.
- Mỗi màn có loading, empty, error và nội dung thành công; disable nút gửi khi đang xử lý, thông báo lỗi dễ hiểu.
- Không biến mọi thư mục thành một lớp abstraction. Tính năng nhỏ có thể chỉ cần một file màn hình và CSS/StyleSheet tương ứng.
- Tên component PascalCase, hàm/biến JavaScript camelCase, Python snake_case. Thư mục scaffold có dấu gạch ngang là tên nhóm; module Python thực tế dùng underscore (ví dụ custom_design.py), không import tên có dấu '-'.
- Không thêm chức năng ngoài scope chỉ vì thấy thư mục. Logout có thể là nút/action, không cần một trang riêng.
- Chỉ comment phần cần giải thích lý do, không comment lại từng dòng hiển nhiên.

## 10. Git và phối hợp
1. Trước task: lấy main mới, tạo nhánh riêng.
```powershell
git switch main
git pull origin main
git switch -c feature/S1-018-product-detail
```
2. Code, tự kiểm tra và commit thay đổi đúng phạm vi.
```powershell
git add .
git commit -m "feat: add product detail"
git push -u origin feature/S1-018-product-detail
```
3. Mở PR về main, ghi task ID, thay đổi, cách test, ảnh UI và tác động API/database. Một người khác review trước merge.
4. Sau merge Trình test theo case, ghi lỗi và retest. Không đánh Done chỉ vì đã push code.

Không force-push main. Không commit .env, key, node_modules, .venv, dữ liệu cá nhân. Người khởi tạo thêm .gitignore trước commit code/thư viện. Lockfile phải commit; dùng npm ci cho thành viên clone. Conflict cần đọc hai thay đổi, không chọn ghi đè toàn bộ cho nhanh.

## 11. Khi nào task được Done?
- Đạt acceptance criteria và đúng thiết kế/phạm vi.
- Phần thay đổi chạy được; web build thành công nếu ảnh hưởng web.
- Đã nối API thật nếu task yêu cầu tích hợp, không chỉ mock.
- Kiểm tra luồng thành công và lỗi liên quan; role sai bị chặn; không làm hỏng luồng đang có.
- PR đã review/merge; cập nhật tài liệu/API/migration khi cần.
- Có bằng chứng test và không còn lỗi chặn task; Trình retest bug đã sửa.

Bug ghi: môi trường, tài khoản/role thử nghiệm, bước tái hiện, mong đợi, thực tế, ảnh/log không chứa secret, mức độ, người xử lý và kết quả retest.
Trình không phải viết automated test thay lập trình viên. Backend developer kiểm tra API/transaction; frontend developer kiểm tra UI và tích hợp; Trình kiểm thử chức năng và tài liệu.

## 12. Lịch và cách cập nhật sprint
Kế hoạch trước đó: Sprint1 28/09–18/10; Sprint2 19/10–01/11; Sprint3 02/11–15/11; Sprint4 16/11–06/12. 07–10/12 dự phòng sửa/retest, 11–14/12 hoàn thiện báo cáo/demo; 15/12 bắt đầu bảo vệ.
★ Nhóm/mentor xác nhận lịch, năng lực thực tế và sprint dài không đều. Đây là kế hoạch, không cam kết chắc chắn đủ thời gian.
Cập nhật task và impediment thường xuyên; báo ngay khi vướng API, ảnh thiết kế hoặc dịch vụ ngoài. Không chờ cuối sprint mới ghép frontend/backend.

## 13. ★ Những điểm cần nhóm duyệt trước khi code phần liên quan
| Điểm | Cần chốt |
|---|---|
| Phiên bản môi trường | Node/Python/Expo và dependency tương thích, chạy được trên máy nhóm |
| Database/API | ERD, model, role, payload, trạng thái, trách nhiệm mỗi API |
| Thanh toán | VNPay sandbox hay thật; đối soát chuyển khoản tại quầy; điều kiện COD |
| AI | Nhà cung cấp/model, license, chất lượng, thời gian xử lý, chi phí |
| OTP/Google/storage | Tài khoản tích hợp, hạn mức, cấu hình ứng dụng, quyền riêng tư |
| Size | Một bảng size thống nhất, quy tắc gợi ý và trường hợp không đủ dữ liệu |
| Đơn hàng | Phí ship, hủy/trả/hoàn tiền, thời gian giữ tồn, không mặc định số từ bản cũ |
| Custom | Hạn báo giá, đặt cọc hay trả đủ, sửa mẫu, người sản xuất và bàn giao |
| Chat/thông báo | Chatbot phạm vi nào; polling hay realtime; có cần push không |
| Báo cáo | Thế nào là doanh thu, hoàn tiền và tương tác hợp lệ |
| Tiến độ | Bảng task/giờ sau khi tách hai backend, lịch review và người chịu trách nhiệm |

Các điểm ★ chưa được duyệt không được mô tả là đã thống nhất. Khi có quyết định, sửa ngay bảng này và tài liệu liên quan trong cùng PR.

## 14. Gửi cho thành viên thế nào?
Gửi link repository và yêu cầu đọc README trước khi nhận task. Không cần gửi lại bản “thống nhất” cũ nếu nội dung đã được cập nhật tại đây. Vẫn phải đưa bảng sprint và ảnh thiết kế/API contract vào repo hoặc gắn link bản chính xác để thành viên có đầu vào làm việc. Không có link repository thật hoặc tài liệu thật trong các thư mục thì README không tự thay thế được chúng.
