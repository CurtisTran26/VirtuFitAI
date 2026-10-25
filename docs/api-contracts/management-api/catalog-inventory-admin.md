# Management API: catalog, inventory, staff and roles

Base URL: `http://localhost:8001/api/v1`. JSON uses snake_case, UUID string IDs and UTC ISO 8601 timestamps. Errors use `{"error":{"code":"...","message":"...","details":{}}}`. Management staff authenticate with `POST /auth/staff-login` and use its bearer token. Session expiry, logout, hashing and invalidation are shared with App API.

## Access roles

The five seeded roles are `customer`, `sales_staff`, `warehouse_staff`, `designer`, `admin`. Admin manages accounts and role assignments. Admin and Warehouse Staff manage categories, products, size charts and variants. Admin and Warehouse Staff adjust stock and read stock history. Any authenticated role can read catalog and size charts. Admin-created staff accounts cannot choose Customer; only customer signup creates customer accounts. Users cannot grant themselves roles.

## Authentication and account administration

| Method and path | Access | Request | Success |
|---|---|---|---|
| `POST /auth/staff-login` | Public | `{ "phone":"+84901234567", "password":"..." }` | 200 `{ "user":{"id":"uuid","phone":"...","full_name":"...","role":"warehouse_staff"}, "access_token":"...", "token_type":"bearer", "expires_at":"...Z" }` |
| `POST /auth/logout` | Any authenticated | no body | 204 and current session revoked |
| `POST /auth/change-password` | Any authenticated | `{ "current_password":"...","new_password":"at-least-8-chars" }` | 204; all user sessions revoked |
| `POST /auth/password-reset-otp` | Public staff account | `{ "phone":"+84901234567" }` | 202; OTP expires in five minutes |
| `POST /auth/reset-password` | Public + valid OTP | `{ "phone":"...","otp_code":"123456","new_password":"at-least-8-chars" }` | 204; staff sessions revoked |
| `GET /admin/roles` | Admin | — | 200 `{ "items":[{"name":"admin","description":"Administrator"}] }` |
| `GET /admin/users?page=1&limit=20&role=designer` | Admin | — | 200 `{ "items":[{"id":"uuid","phone":"...","full_name":"...","is_active":true,"role":"designer","created_at":"...Z"}],"page":1,"limit":20,"total":1 }` |
| `POST /admin/users` | Admin | `{ "phone":"...","full_name":"...","password":"12-or-more-chars","role":"sales_staff" }` | 201 user fields, role and `is_active` |
| `PATCH /admin/users/{user_id}/role` | Admin | `{ "role":"designer" }` | 200 `{ "id":"uuid","role":"designer" }`; existing sessions revoked |
| `PATCH /admin/users/{user_id}/status?is_active=false` | Admin | — | 200 `{ "id":"uuid","is_active":false }`; sessions revoked when deactivated |

## Catalog

| Method and path | Access | Request | Success |
|---|---|---|---|
| `GET /categories?page=1&limit=20` | Authenticated | — | paginated `items` with id, name, description, is_active, created_at |
| `POST /categories` | Admin, Warehouse | `{ "name":"Áo thun","description":"...","is_active":true }` | 201 category |
| `PATCH /categories/{id}` | Admin, Warehouse | same fields as create | 200 category |
| `DELETE /categories/{id}` | Admin, Warehouse | — | 204; soft archive (`is_active=false`) |
| `GET /products?page=1&limit=20&category_id={uuid}` | Authenticated | — | paginated items with category_name, price_vnd (integer), sku, image_url and is_active |
| `POST /products` | Admin, Warehouse | `{ "category_id":"uuid","name":"...","description":"...","price_vnd":120000,"sku":"SKU-1","image_url":null,"is_active":true }` | 201 product |
| `PATCH /products/{id}` | Admin, Warehouse | same fields as create | 200 product |
| `DELETE /products/{id}` | Admin, Warehouse | — | 204; soft archive |
| `GET /size-charts?category_id={uuid}` | Authenticated | — | 200 `{ "items":[{"id":"uuid","category_id":"uuid","name":"...","measurements":[{"size":"M","chest_cm":96}],"created_at":"...Z"}] }` |
| `POST /size-charts` | Admin, Warehouse | `{ "category_id":"uuid","name":"Size chart","measurements":[{"size":"M","chest_cm":96}] }` | 201 chart |
| `PUT /size-charts/{id}` | Admin, Warehouse | same fields as create | 200 chart |
| `DELETE /size-charts/{id}` | Admin, Warehouse | — | 204 |
| `POST /products/{product_id}/variants` | Admin, Warehouse | `{ "product_id":"uuid","size":"M","color":"Black","sku":"SKU-M-BLK" }` | 201 variant with `stock_on_hand:0` |

## Inventory

| Method and path | Access | Request | Success |
|---|---|---|---|
| `POST /inventory/variants/{variant_id}/adjustments` | Admin, Warehouse | `{ "delta":5,"reason":"Counted at receiving" }` | 201 audit entry: id, variant_id, changed_by, delta, quantity_before, quantity_after, reason, created_at |
| `GET /inventory/variants/{variant_id}/adjustments?page=1&limit=20` | Admin, Warehouse | — | 200 paginated audit entries |
| `GET /inventory/variants?page=1&limit=20` | Admin, Warehouse | — | 200 paginated variant quantities with product name, SKU, size, color and updated_at |

Stock adjustment locks the variant row, applies the delta and records before/after quantities in one transaction. Negative stock returns 409 `OUT_OF_STOCK`; zero delta is rejected. Catalog duplicate keys return 409. General errors: 401 unauthenticated/expired, 403 wrong role, 404 missing record, 422 invalid input. Interactive OpenAPI: `/api/v1/docs`.
