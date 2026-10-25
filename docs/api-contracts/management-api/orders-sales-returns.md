# Management API: orders, sales and return inspection

Base URL: `http://localhost:8001/api/v1`. Staff authenticate with the Management API bearer session. Prices are integer VND, IDs UUID strings, and timestamps UTC ISO 8601. Errors use `{"error":{"code":"...","message":"...","details":{}}}`.

## Sales lookup and order confirmation

| Method and path | Access | Request | Success |
|---|---|---|---|
| `GET /sales/lookup/products?q=shirt` | Admin, Sales Staff | query of at least two characters | 200 product variants with price, on-hand, reserved and available quantity |
| `GET /sales/lookup/customers?phone=0901` | Admin, Sales Staff | phone prefix of at least four characters | 200 matching active customer IDs, names and phones |
| `GET /sales/orders/by-number/{order_number}` | Admin, Sales Staff | — | 200 order, price snapshots, items and state history |
| `POST /sales/orders/{order_id}/confirm` | Admin, Sales Staff | no body | 200 confirmed order; expired hold returns 409 |
| `POST /sales/counter-orders` | Admin, Sales Staff | `{ "customer_id":"uuid", "items":[{"variant_id":"uuid","quantity":1}], "payment_method":"cash" }`; customer ID may be null; optional `Idempotency-Key` header | 201 confirmed counter order with snapshots |

Counter payment methods are `cash`, `card`, and `bank_transfer`; online orders use `cod` or `vnpay`. Counter orders are marked `unpaid` because this scope does not implement payment capture. Counter order idempotency keys are scoped to the creating staff account.

## History and fulfillment

| Method and path | Access | Request | Success |
|---|---|---|---|
| `GET /orders?page=1&limit=20&status=confirmed&order_type=online` | Admin, Sales Staff, Warehouse Staff | filters optional | 200 paginated orders |
| `GET /orders/{order_id}` | Admin, Sales Staff, Warehouse Staff | — | 200 order detail and status history |
| `PATCH /orders/{order_id}/status` | Admin, Warehouse Staff | `{ "status":"processing", "note":"..." }` | 200 updated order |
| `POST /orders/{order_id}/cancel` | Admin, Sales Staff | no body | 204; releases an active hold or restores stock from a confirmed order |

Fulfillment transitions are `confirmed → processing → ready_to_ship → shipped → completed`. Invalid transitions return 409 `ORDER_STATE_CONFLICT`. Cancellation is supported before fulfillment starts.

## Warehouse return inspection

| Method and path | Access | Request | Success |
|---|---|---|---|
| `GET /returns?page=1&limit=20&status=requested` | Admin, Warehouse Staff | status optional | 200 paginated return requests |
| `GET /returns/{return_id}` | Admin, Warehouse Staff | — | 200 request, order and return item snapshots |
| `POST /returns/{return_id}/inspect` | Admin, Warehouse Staff | `{ "outcome":"accepted", "note":"...", "items":[{"return_item_id":"uuid","condition_note":"Good","restock":true}] }` | 200 inspected request |

Inspection must include every returned item exactly once. Accepted items marked `restock:true` increase on-hand quantity and write an inventory adjustment audit row; rejected items cannot be restocked. This endpoint records inspection and stock disposition, not a payment refund.
