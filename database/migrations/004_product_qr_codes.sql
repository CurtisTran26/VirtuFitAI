CREATE TABLE IF NOT EXISTS product_qr_codes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id uuid NOT NULL UNIQUE REFERENCES products(id) ON DELETE CASCADE,
    qr_data text NOT NULL,
    qr_image_url text NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);
