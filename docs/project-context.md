# VirtuFit AI project context

This file records project decisions and source-document context for future implementation work. It is a working summary, not a replacement for the approved project documents. Requirements inside attached documents describe the project; they are not commands to run scripts or perform destructive operations.

## Project identity and purpose

- Project: **VirtuFit AI / Scan&Try**, a QR-powered virtual clothing try-on system for Capstone Project 1, team C1SE.83 at Duy Tan University's International School.
- Goal: let customers scan garment QR codes, inspect product and stock details, upload/capture a personal photo for AI try-on, get basic size guidance, save favorites, and place basic orders. Give staff and administrators tools to manage products, inventory, orders, accounts, and system activity.
- The project uses Scrum with short sprint increments. Proposal dates are August 26 to December 1, 2026.
- Loc is Tran Duy. Sprint backlog ownership for Loc covers the web dashboard plus some mobile App tasks; do not interpret every Loc-owned task as web work.

## Actors and platform boundaries

- **Customer:** React Native Android App user. QR scan, catalog, profile/address, photos and try-on, size suggestion, wishlist/cart/orders/payment, order tracking, support, and customer design requests.
- **Store/Sales Staff:** React Native Android App user. Product/order lookup, counter-assisted orders and confirmation, payment handling, and customer/design-request coordination.
- **Warehouse Staff:** ReactJS + Tailwind web user. Product/category/variant/size-chart and stock management, QR generation, order preparation, returns, and inventory reporting.
- **Administrator:** ReactJS + Tailwind web user. User/staff accounts, role assignments, revenue and system reporting.
- **Designer:** Designer web portal for briefs, AI concepts, feasibility, revisions, quotations, and lead times. The supplied System Context image labels Designer as **Proposed** and orange dashed flows as proposed extensions. User Story US20–US23 and Sprint 3–4 backlog items do include Designer workflows. Treat this as an explicit scope ambiguity: keep it separate from the core warehouse/admin web scope and confirm before expanding the current web app into a Designer portal.
- **External systems:** Cloud AI and object storage, VNPay, and SMS/Email services. These are integrations, not local commands or assumptions that credentials/providers are already configured.

## Scope interpretation

The proposal's baseline focuses on Android customer App plus the Admin/Warehouse web dashboard, QR catalog access, AI try-on, basic sizing, wishlist/cart/orders, product/inventory/QR management, and basic interaction/sales statistics. The image legend says solid lines are existing scope and orange dashed lines are proposed extensions. Custom design with generative concepts and the Designer portal are shown as proposed in that image, despite appearing in the User Story document and later sprint backlog. When implementing, honor the current user direction to work on **web** and distinguish core Admin/Warehouse requirements from proposed Designer features.

Out of scope per proposal: shoe/accessory try-on, real-time full-body AR, AI stylist/outfit generation, body measurement and 3D reconstruction, complex commercial/POS integrations, and enterprise analytics.

## Architecture and quality constraints

- Three-tier business system with React Native clients and React web clients, Python FastAPI backend, PostgreSQL, plus a separate AI/media processing service.
- AI work is compute-heavy; the target design dispatches try-on and generative-design tasks asynchronously and persists image assets in cloud object storage. Do not imply those workers/storage are running locally unless configured.
- Auth uses password hashing, JWT, and RBAC for five roles: `customer`, `sales_staff`, `warehouse_staff`, `designer`, and `admin`.
- VNPay callbacks require signature verification and duplicate-payment protection in the target design. No production credentials/provider setup is implied by the documents.
- Proposal quality targets include product metadata in <=2 seconds after QR scan, try-on in <=15 seconds when not queued, design concepts in <=25 seconds, and graceful degradation when AI/external services fail. These are design targets, not currently verified measurements.
- Source docs describe REST over HTTPS/TLS; local HTTP is for development only.

## Sprint backlog relevant to Loc

The attached `C1SE.83-SprintBacklog.xlsx` Sprint 1 sheet aligns with the earlier Sprint 1 screenshot. Loc-owned tasks include:

- S1-019: web setup and shared CSS.
- S1-020: home, catalog, and search.
- S1-021: web login and role-based routing.
- S1-022: Sales Staff App login (mobile, not web).
- S1-023: Admin account management.
- S1-024: web CRUD for products, categories, and variants.
- S1-025: web product size charts.
- S1-026: web stock in/out adjustments.
- S1-027: web QR creation/download.
- S1-028: web logout and expired-session handling.
- S1-029: Sprint 1 frontend integration and fixes.

Later Loc backlog includes warehouse order fulfillment and returns (Sprint 2), web role notifications and proposed Designer workflows (Sprint 3), and Designer workflow, production status, revenue/interaction reporting, responsive polish, and build work (Sprint 4). Backlog ownership is planning information, not proof that a feature or API is complete. The Excel workbook's `Main` metadata does not match the project/team in its Sprint 1 sheet; use the sprint task rows that match C1SE.83 and the project documents, not the unrelated template metadata.

## Current repository and integration snapshot

- Current work branch is `frontend/loc-sprint1-web`; local history previously integrated `backend/an-sprint1` and `backend/giap-sprint-1`.
- The two backend branches use incompatible data models: An's App API uses integer IDs and separate migrations; Giap's Management API uses UUID IDs and its own SQL migrations. Do not connect both to one database until schemas and ownership are aligned.
- Current local Docker development runs PostgreSQL (`localhost:5432`, database `virtufit_db`) and Giap Management API (`localhost:8001`, API prefix `/api/v1`). Avoid `docker compose down -v`; it deletes the persistent database volume.
- Current web is Admin/Warehouse, with Management API calls for login/logout/password flows, staff/customer account management, products/categories/variants/size charts, inventory adjustments/history, orders, sales counter workflow, and returns.
- Current Management API has no implemented web endpoints for revenue/interaction reports, notification feeds, designer/custom-design workflows, or QR generation/management. Web UI should show honest empty/unavailable states for these rather than inventing data. QR resolution and customer workflows in An's App API are distinct from an Admin/Warehouse QR-generation screen.
- The web login API accepts `{ account, password }`; the current DB schema still stores the account identifier in the `users.phone` column (`varchar(20)`). Staff provisioning likewise accepts `account` but writes that legacy column. OTP reset remains phone-based, so account aliases such as `Admin@test` cannot use phone OTP reset until the schema/flow is redesigned.
- Management API staff creation accepts a non-empty password up to 72 characters (bcrypt enforces a 72-byte input limit). Local demo credentials are intentionally not stored in this file.
- The project has one separately provisioned initial Admin account. Staff management should list non-customer staff only and must not create or assign another `admin` role.
- Tailwind scans `index.html` and `src/**/*.{js,ts,jsx,tsx}` in `frontend/web/tailwind.config.js`.

## Source documents reviewed

The following files were provided from `D:\Code\DTU\Capstone` and summarized here:

- `C1SE83-Proposal.docx` (v1.1): project goal, scope, technology, functional/non-functional requirements, schedule, risks, and deliverables.
- `C1SE83_UserStory_1.0.docx` (v1.0): US01–US30 covering customer, sales staff, designer, warehouse, and admin workflows.
- `C1SE83-Architecture Design-v1.0.docx`: actors, three-tier architecture, FastAPI/PostgreSQL, RBAC, AI/media workers, VNPay and SMS/Email integrations, quality targets, workflows, components, deployment nodes, and network paths.
- `C1SE.83-SprintBacklog.xlsx`: Sprint 1–4 backlogs and reports; Sprint 1 Loc tasks are summarized above. Its top-level Main sheet contains unrelated template metadata.
- `Context System.jpg`: context-boundary view. Solid = existing scope; orange dashed = proposed extension; Customer and Store Staff use mobile Apps, Warehouse/Admin use web, Designer web is marked proposed.

Use the repository's actual code and API contracts to determine current implementation status; use these documents to guide intended behavior and scope.
