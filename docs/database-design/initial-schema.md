# Initial database schema

PostgreSQL 15+, UUID primary keys, UTC `timestamptz`. Both APIs share the same database and schema. Migrations are the source of truth in `database/migrations/`; initial fixed roles are in `database/seeds/001_roles.sql`.

| Table | Purpose and constraints |
|---|---|
| `roles` | Exactly the five application roles; unique name. |
| `users` | Unique phone, password hash, role FK, activation and verification timestamps. Customer role is server assigned. |
| `user_sessions` | SHA-256 token digest, expiry and revocation; no bearer token stored in plaintext. |
| `otp_challenges` | Phone, purpose, digest, five-minute expiry, attempt count and one-time consumption. |
| `categories`, `products` | Catalog; products use integer VND, unique SKU and soft archive. |
| `size_charts` | Category-linked JSON measurement rows, e.g. `[{"size":"M","chest_cm":96}]`. |
| `product_variants` | Product, size, color, unique SKU, nonnegative on-hand and held quantities; product/size/color unique. |
| `inventory_adjustments` | Immutable actor, delta, before/after and reason audit record. |
| `wishlists` | Composite `(user_id, product_id)` key makes add idempotent. |
| `orders`, `order_items` | Order lifecycle, customer/address/price snapshots and immutable line-price snapshots. |
| `inventory_reservations` | Per-order stock holds with active/consumed/released lifecycle and expiry. |
| `order_status_history` | Actor, transition, note and timestamp for every order state change. |
| `return_requests`, `return_items` | Customer return requests, quantities and warehouse inspection/restock decisions. |

Migration bootstrap and seed commands are in `database/README.md`. Schema changes must be new numbered SQL migrations; do not edit an applied migration.
