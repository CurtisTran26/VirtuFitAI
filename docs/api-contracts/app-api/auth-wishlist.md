# App API: authentication and wishlist

Base URL: `http://localhost:8000/api/v1`. JSON fields use snake_case; IDs are UUID strings; timestamps are UTC ISO 8601. Every error is `{"error":{"code":"...","message":"...","details":{}}}`. Bearer sessions expire after `SESSION_TTL_HOURS` (default 24) and are stored as SHA-256 digests so logout and password changes invalidate them.

| Method and path | Access | Request | Success |
|---|---|---|---|
| `POST /auth/otp` | Public | `{ "phone":"+84901234567", "purpose":"register" }` or `reset_password` | 202 `{ "message":"OTP request accepted" }` |
| `POST /auth/register` | Public, customer only | `{ "phone":"+84901234567", "full_name":"Linh", "password":"at-least-8-chars", "otp_code":"123456" }` | 201 `{ "user":{"id":"uuid","phone":"...","full_name":"Linh","role":"customer"}, "access_token":"...", "token_type":"bearer", "expires_at":"...Z" }` |
| `POST /auth/login` | Public | `{ "phone":"...", "password":"..." }` | 200 user and bearer session (same shape as register) |
| `POST /auth/reset-password` | Public + valid OTP | `{ "phone":"...", "otp_code":"123456", "new_password":"at-least-8-chars" }` | 204; all prior sessions revoked |
| `POST /auth/change-password` | Any authenticated user | `{ "current_password":"...", "new_password":"at-least-8-chars" }` | 204; all sessions revoked |
| `POST /auth/logout` | Any authenticated user | no body | 204; presented session revoked |
| `GET /wishlist?page=1&limit=20` | Any authenticated user | — | 200 `{ "items":[{"id":"uuid","name":"...","price_vnd":120000,"image_url":null,"created_at":"...Z"}], "page":1,"limit":20,"total":1 }` |
| `PUT /wishlist/{product_id}` | Any authenticated user | — | 204; idempotent |
| `DELETE /wishlist/{product_id}` | Any authenticated user | — | 204; idempotent |

OTP lifetime is five minutes, max five requests per phone/hour and max five verification attempts. OTP is one-use. `OTP_DEBUG=true` exposes a code only for local development; production requires a phone OTP provider adapter and must leave this off. Phone verification is required for customer registration; customer role is assigned server-side. Login errors do not reveal whether a phone exists. Passwords must be at least eight characters. Reset and change invalidate existing sessions.

Common status codes: 400 invalid OTP/current password, 401 invalid credentials/session, 409 duplicate phone, 422 invalid input, 429 OTP rate limit. OpenAPI: `/api/v1/openapi.json`.
