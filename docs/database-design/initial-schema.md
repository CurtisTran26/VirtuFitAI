# Initial database schema

PostgreSQL 15+, UUID primary keys, UTC `timestamptz`. Both APIs share the same database and schema. The single source of truth is `database/migrations/001_initial.sql`; initial fixed roles are in `database/seeds/001_roles.sql`.

| Table | Purpose and constraints |
|---|---|
| `roles` | Exactly the five application roles; unique name. |
| `users` | Unique phone, password hash, role FK, activation and verification timestamps. Customer role is server assigned. |
| `user_sessions` | SHA-256 token digest, expiry and revocation; no bearer token stored in plaintext. |
| `otp_challenges` | Phone, purpose, digest, five-minute expiry, attempt count and one-time consumption. |
| `categories`, `products` | Catalog; products use integer VND, unique SKU and soft archive. |
| `size_charts` | Category-linked JSON measurement rows, e.g. `[{"size":"M","chest_cm":96}]`. |
| `product_variants` | Product, size, color, unique SKU, nonnegative stock; product/size/color unique. |
| `inventory_adjustments` | Immutable actor, delta, before/after and reason audit record. |
| `wishlists` | Composite `(user_id, product_id)` key makes add idempotent. |

Migration bootstrap and seed commands are in `database/README.md`. Schema changes must be new numbered SQL migrations; do not edit an applied migration. The initial migration intentionally contains only tables needed for the requested auth, catalog, inventory and wishlist scope.
