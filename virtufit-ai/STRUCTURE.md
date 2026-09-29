# Cấu trúc thư mục đầy đủ

```text
virtufit-ai/
├── ai/
│   ├── design-generation/
│   ├── evaluation/
│   ├── image-processing/
│   ├── image-validation/
│   ├── job-handling/
│   ├── providers/
│   ├── tests/
│   └── try-on/
├── backend/
│   ├── app-api/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   ├── integrations/
│   │   │   │   ├── ai-service/
│   │   │   │   ├── google-login/
│   │   │   │   ├── object-storage/
│   │   │   │   ├── phone-otp/
│   │   │   │   └── vnpay/
│   │   │   ├── routers/
│   │   │   │   ├── auth/
│   │   │   │   ├── cart/
│   │   │   │   ├── catalog/
│   │   │   │   ├── chat/
│   │   │   │   ├── custom-design/
│   │   │   │   ├── notifications/
│   │   │   │   ├── orders/
│   │   │   │   ├── payments/
│   │   │   │   ├── profiles/
│   │   │   │   ├── qr-scan/
│   │   │   │   ├── returns/
│   │   │   │   ├── sales/
│   │   │   │   ├── size-recommendation/
│   │   │   │   ├── try-on/
│   │   │   │   └── wishlist/
│   │   │   ├── schemas/
│   │   │   │   ├── auth/
│   │   │   │   ├── cart/
│   │   │   │   ├── catalog/
│   │   │   │   ├── chat/
│   │   │   │   ├── custom-design/
│   │   │   │   ├── notifications/
│   │   │   │   ├── orders/
│   │   │   │   ├── payments/
│   │   │   │   ├── profiles/
│   │   │   │   ├── qr-scan/
│   │   │   │   ├── returns/
│   │   │   │   ├── sales/
│   │   │   │   ├── size-recommendation/
│   │   │   │   ├── try-on/
│   │   │   │   └── wishlist/
│   │   │   └── services/
│   │   │       ├── auth/
│   │   │       ├── cart/
│   │   │       ├── catalog/
│   │   │       ├── chat/
│   │   │       ├── custom-design/
│   │   │       ├── notifications/
│   │   │       ├── orders/
│   │   │       ├── payments/
│   │   │       ├── profiles/
│   │   │       ├── qr-scan/
│   │   │       ├── returns/
│   │   │       ├── sales/
│   │   │       ├── size-recommendation/
│   │   │       ├── try-on/
│   │   │       └── wishlist/
│   │   └── tests/
│   │       ├── integration/
│   │       └── unit/
│   ├── management-api/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   ├── integrations/
│   │   │   │   ├── ai-service/
│   │   │   │   ├── object-storage/
│   │   │   │   └── phone-otp/
│   │   │   ├── routers/
│   │   │   │   ├── auth/
│   │   │   │   ├── categories/
│   │   │   │   ├── chat/
│   │   │   │   ├── custom-design/
│   │   │   │   ├── inventory/
│   │   │   │   ├── notifications/
│   │   │   │   ├── orders/
│   │   │   │   ├── production/
│   │   │   │   ├── products/
│   │   │   │   ├── profiles/
│   │   │   │   ├── qr-codes/
│   │   │   │   ├── quotations/
│   │   │   │   ├── reports/
│   │   │   │   ├── returns/
│   │   │   │   ├── roles/
│   │   │   │   ├── staff/
│   │   │   │   └── users/
│   │   │   ├── schemas/
│   │   │   │   ├── auth/
│   │   │   │   ├── categories/
│   │   │   │   ├── chat/
│   │   │   │   ├── custom-design/
│   │   │   │   ├── inventory/
│   │   │   │   ├── notifications/
│   │   │   │   ├── orders/
│   │   │   │   ├── production/
│   │   │   │   ├── products/
│   │   │   │   ├── profiles/
│   │   │   │   ├── qr-codes/
│   │   │   │   ├── quotations/
│   │   │   │   ├── reports/
│   │   │   │   ├── returns/
│   │   │   │   ├── roles/
│   │   │   │   ├── staff/
│   │   │   │   └── users/
│   │   │   └── services/
│   │   │       ├── auth/
│   │   │       ├── categories/
│   │   │       ├── chat/
│   │   │       ├── custom-design/
│   │   │       ├── inventory/
│   │   │       ├── notifications/
│   │   │       ├── orders/
│   │   │       ├── production/
│   │   │       ├── products/
│   │   │       ├── profiles/
│   │   │       ├── qr-codes/
│   │   │       ├── quotations/
│   │   │       ├── reports/
│   │   │       ├── returns/
│   │   │       ├── roles/
│   │   │       ├── staff/
│   │   │       └── users/
│   │   └── tests/
│   │       ├── integration/
│   │       └── unit/
│   └── shared/
│       ├── authentication/
│       ├── database/
│       ├── design-rules/
│       ├── enums/
│       ├── exceptions/
│       ├── inventory-rules/
│       ├── models/
│       ├── order-rules/
│       ├── payment-rules/
│       ├── permissions/
│       └── utils/
├── database/
│   ├── diagrams/
│   ├── migrations/
│   ├── schema/
│   └── seeds/
├── docs/
│   ├── ai-evaluation/
│   ├── api-contracts/
│   │   ├── app-api/
│   │   └── management-api/
│   ├── architecture/
│   ├── bug-reports/
│   ├── database-design/
│   ├── defense-slides/
│   ├── demo/
│   ├── deployment-guide/
│   ├── final-report/
│   ├── meeting-notes/
│   ├── product-backlog/
│   ├── proposal/
│   ├── sprint-backlogs/
│   │   ├── sprint-1/
│   │   ├── sprint-2/
│   │   ├── sprint-3/
│   │   └── sprint-4/
│   ├── srs/
│   ├── system-context/
│   ├── test-cases/
│   ├── test-plan/
│   ├── test-reports/
│   ├── ui-design/
│   │   ├── mobile/
│   │   └── web/
│   ├── use-cases/
│   └── user-guide/
├── frontend/
│   ├── mobile/
│   │   └── src/
│   │       ├── assets/
│   │       │   ├── icons/
│   │       │   └── images/
│   │       ├── components/
│   │       ├── config/
│   │       ├── context/
│   │       ├── hooks/
│   │       ├── navigation/
│   │       ├── screens/
│   │       │   ├── auth/
│   │       │   │   ├── forgot-password/
│   │       │   │   ├── google-login/
│   │       │   │   ├── login/
│   │       │   │   ├── phone-otp/
│   │       │   │   ├── register/
│   │       │   │   └── reset-password/
│   │       │   ├── customer/
│   │       │   │   ├── cancel-order/
│   │       │   │   ├── cart/
│   │       │   │   ├── catalog/
│   │       │   │   ├── change-password/
│   │       │   │   ├── chat/
│   │       │   │   ├── checkout/
│   │       │   │   ├── custom-design/
│   │       │   │   │   ├── ai-concepts/
│   │       │   │   │   ├── approval/
│   │       │   │   │   ├── create-request/
│   │       │   │   │   ├── order-confirmation/
│   │       │   │   │   ├── progress/
│   │       │   │   │   ├── quotation/
│   │       │   │   │   ├── request-detail/
│   │       │   │   │   └── revisions/
│   │       │   │   ├── edit-profile/
│   │       │   │   ├── filters/
│   │       │   │   ├── home/
│   │       │   │   ├── notifications/
│   │       │   │   ├── order-detail/
│   │       │   │   ├── order-tracking/
│   │       │   │   ├── orders/
│   │       │   │   ├── payment/
│   │       │   │   ├── payment-result/
│   │       │   │   ├── product-detail/
│   │       │   │   ├── profile/
│   │       │   │   ├── qr-scanner/
│   │       │   │   ├── return-request/
│   │       │   │   ├── search/
│   │       │   │   ├── size-recommendation/
│   │       │   │   ├── try-on/
│   │       │   │   │   ├── history/
│   │       │   │   │   ├── processing/
│   │       │   │   │   ├── result/
│   │       │   │   │   └── upload-photo/
│   │       │   │   └── wishlist/
│   │       │   └── sales/
│   │       │       ├── cash-payment/
│   │       │       ├── create-counter-order/
│   │       │       ├── create-custom-order/
│   │       │       ├── custom-design-handover/
│   │       │       ├── customer-support/
│   │       │       ├── dashboard/
│   │       │       ├── order-confirmation/
│   │       │       ├── order-detail/
│   │       │       ├── orders/
│   │       │       ├── product-lookup/
│   │       │       ├── receipt/
│   │       │       ├── stock-lookup/
│   │       │       └── transfer-payment/
│   │       ├── services/
│   │       │   └── api/
│   │       ├── styles/
│   │       └── utils/
│   └── web/
│       └── src/
│           ├── assets/
│           │   ├── icons/
│           │   └── images/
│           ├── components/
│           ├── config/
│           ├── context/
│           ├── hooks/
│           ├── layouts/
│           ├── pages/
│           │   ├── admin/
│           │   │   ├── customer-accounts/
│           │   │   ├── dashboard/
│           │   │   ├── interaction-reports/
│           │   │   ├── revenue-reports/
│           │   │   ├── roles-permissions/
│           │   │   └── staff-accounts/
│           │   ├── auth/
│           │   │   ├── forgot-password/
│           │   │   ├── login/
│           │   │   ├── phone-otp/
│           │   │   └── reset-password/
│           │   ├── common/
│           │   │   ├── change-password/
│           │   │   ├── chat/
│           │   │   ├── forbidden/
│           │   │   ├── not-found/
│           │   │   ├── notifications/
│           │   │   └── profile/
│           │   ├── designer/
│           │   │   ├── ai-concepts/
│           │   │   ├── customer-approvals/
│           │   │   ├── dashboard/
│           │   │   ├── design-requests/
│           │   │   ├── design-revisions/
│           │   │   ├── feasibility-review/
│           │   │   ├── production-updates/
│           │   │   ├── quotations/
│           │   │   └── request-detail/
│           │   └── warehouse/
│           │       ├── categories/
│           │       ├── custom-order-detail/
│           │       ├── custom-orders/
│           │       ├── dashboard/
│           │       ├── inventory/
│           │       ├── order-detail/
│           │       ├── orders/
│           │       ├── packing/
│           │       ├── product-images/
│           │       ├── product-variants/
│           │       ├── products/
│           │       ├── qr-codes/
│           │       ├── returns/
│           │       ├── shipping-updates/
│           │       ├── size-charts/
│           │       └── stock-adjustments/
│           ├── routes/
│           ├── services/
│           │   └── api/
│           ├── styles/
│           └── utils/
├── infra/
│   ├── deployment/
│   ├── docker/
│   └── environments/
└── tests/
    ├── end-to-end/
    │   ├── admin/
    │   ├── customer/
    │   ├── designer/
    │   ├── sales/
    │   └── warehouse/
    ├── integration/
    │   ├── app-web-sync/
    │   └── custom-order-flow/
    ├── performance/
    ├── postman/
    │   ├── app-api/
    │   └── management-api/
    ├── security/
    └── test-data/
```
