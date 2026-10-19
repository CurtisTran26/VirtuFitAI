# Database bootstrap

PostgreSQL 15+ is the shared database for both APIs. Apply SQL migrations in filename order exactly once; migration files are immutable after deployment. Then run seed SQL in filename order.

```powershell
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/001_initial.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f database/seeds/001_roles.sql
```

The migration adds the five fixed business roles, phone accounts, hashed revocable sessions, one-time OTP challenges, catalog/size data, variants, inventory audit history, and wishlists. Never put credentials or real account data in seeds. Create the initial admin through a private provisioning procedure after deployment.
