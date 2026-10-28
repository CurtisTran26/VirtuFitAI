# Database bootstrap

PostgreSQL 15+ is the shared database for both APIs. Apply SQL migrations in filename order exactly once; migration files are immutable after deployment. Then run seed SQL in filename order.

```powershell
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/001_initial.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/002_orders_returns.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/003_catalog_options.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/004_product_qr_codes.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/seeds/001_roles.sql
```

Migration `002_orders_returns.sql` adds order and return snapshots/history plus `reserved_quantity` for variant holds. Migration `004_product_qr_codes.sql` stores QR payloads and public image URLs against UUID product IDs. Never put credentials or real account data in seeds. Create the initial admin through a private provisioning procedure after deployment.
