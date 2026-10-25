# App API: orders and customer returns

Base URL: `http://localhost:8000/api/v1`. All money fields are integer VND, IDs are UUID strings, timestamps are UTC ISO 8601, and errors use `{"error":{"code":"...","message":"...","details":{}}}`. Customer orders snapshot item name, SKU, size, color, unit price, shipping address, and totals when created. Prices and totals are calculated by the server.

## Orders

| Method and path | Access | Request | Success |
|---|---|---|---|
| `POST /orders` | Customer | `{ "items":[{"variant_id":"uuid","quantity":2}], "payment_method":"cod", "shipping_address":{"name":"...","phone":"...","address":"..."} }`; optional `Idempotency-Key` header | 201 order with item snapshots, totals, `status:"pending_confirmation"`, `hold_expires_at` |
| `GET /orders?page=1&limit=20` | Customer | — | 200 `{ "items":[...], "page":1, "limit":20, "total":1 }` |
| `GET /orders/{order_id}` | Order owner | — | 200 order details and item snapshots |
| `GET /orders/{order_id}/history` | Order owner | — | 200 `{ "items":[{"from_status":null,"to_status":"pending_confirmation","note":"...","created_at":"...Z"}] }` |
| `POST /orders/{order_id}/cancel` | Order owner | no body | 204; releases active hold and records the transition |

New online orders hold available stock for 15 minutes. `available_quantity = stock_on_hand - reserved_quantity`. Confirmed orders deduct held quantity from on-hand stock. Holds expire lazily when order creation or order listing runs; attempting to confirm an expired hold returns 409 `ORDER_HOLD_EXPIRED`. Customer cancellation is allowed while the order is pending confirmation. The `Idempotency-Key` is scoped to the authenticated customer.

Order statuses: `pending_confirmation`, `confirmed`, `processing`, `ready_to_ship`, `shipped`, `completed`, `cancelled`, `expired`. A duplicate variant in one request is rejected. Insufficient available stock returns 409 `OUT_OF_STOCK`.

## Returns

| Method and path | Access | Request | Success |
|---|---|---|---|
| `POST /returns` | Customer, completed order owner | `{ "order_id":"uuid", "reason":"...", "items":[{"order_item_id":"uuid","quantity":1}] }` | 201 `{ "id":"uuid", "order_id":"uuid", "status":"requested" }` |
| `GET /returns?page=1&limit=20` | Customer | — | 200 paginated requests |
| `GET /returns/{return_id}` | Request owner | — | 200 request and item inspection results |

Requested quantities cannot exceed the ordered quantity less quantities in other non-rejected return requests. A return is accepted or rejected by warehouse inspection in Management API. Acceptance does not issue a payment refund; payment/refund processing is outside this API scope.
