ALTER TABLE product_variants
    ADD COLUMN reserved_quantity integer NOT NULL DEFAULT 0
    CHECK (reserved_quantity >= 0 AND reserved_quantity <= stock_on_hand);

CREATE TABLE orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number varchar(40) UNIQUE NOT NULL,
    customer_id uuid REFERENCES users(id) ON DELETE SET NULL,
    created_by uuid NOT NULL REFERENCES users(id),
    order_type text NOT NULL CHECK (order_type IN ('online', 'counter')),
    status text NOT NULL CHECK (status IN ('pending_confirmation', 'confirmed', 'processing', 'ready_to_ship', 'shipped', 'completed', 'cancelled', 'expired')),
    payment_method text NOT NULL CHECK (payment_method IN ('cod', 'vnpay', 'cash', 'card', 'bank_transfer')),
    payment_status text NOT NULL DEFAULT 'unpaid' CHECK (payment_status IN ('unpaid', 'paid', 'refunded')),
    address_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
    subtotal_vnd bigint NOT NULL CHECK (subtotal_vnd >= 0),
    discount_vnd bigint NOT NULL DEFAULT 0 CHECK (discount_vnd >= 0),
    total_vnd bigint NOT NULL CHECK (total_vnd >= 0),
    idempotency_key varchar(128),
    hold_expires_at timestamptz,
    confirmed_at timestamptz,
    cancelled_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (total_vnd = subtotal_vnd - discount_vnd)
);
CREATE UNIQUE INDEX orders_idempotency_idx ON orders(created_by, idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX orders_customer_history_idx ON orders(customer_id, created_at DESC);
CREATE INDEX orders_status_idx ON orders(status, created_at DESC);

CREATE TABLE order_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id uuid REFERENCES products(id) ON DELETE SET NULL,
    variant_id uuid REFERENCES product_variants(id) ON DELETE SET NULL,
    product_name_snapshot varchar(180) NOT NULL,
    sku_snapshot varchar(80) NOT NULL,
    size_snapshot varchar(30) NOT NULL,
    color_snapshot varchar(50) NOT NULL DEFAULT '',
    unit_price_vnd bigint NOT NULL CHECK (unit_price_vnd >= 0),
    quantity integer NOT NULL CHECK (quantity > 0),
    line_total_vnd bigint NOT NULL CHECK (line_total_vnd >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(order_id, variant_id)
);
CREATE INDEX order_items_order_idx ON order_items(order_id);

CREATE TABLE inventory_reservations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    variant_id uuid NOT NULL REFERENCES product_variants(id) ON DELETE RESTRICT,
    quantity integer NOT NULL CHECK (quantity > 0),
    status text NOT NULL CHECK (status IN ('active', 'consumed', 'released')),
    expires_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(order_id, variant_id)
);
CREATE INDEX inventory_reservations_expiry_idx ON inventory_reservations(status, expires_at) WHERE status = 'active';

CREATE TABLE order_status_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    changed_by uuid REFERENCES users(id) ON DELETE SET NULL,
    from_status text,
    to_status text NOT NULL,
    note text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX order_status_history_order_idx ON order_status_history(order_id, created_at DESC);

CREATE TABLE return_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    customer_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reason text NOT NULL,
    status text NOT NULL DEFAULT 'requested' CHECK (status IN ('requested', 'accepted', 'rejected')),
    inspected_by uuid REFERENCES users(id) ON DELETE SET NULL,
    inspection_note text NOT NULL DEFAULT '',
    inspected_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX return_requests_status_idx ON return_requests(status, created_at DESC);
CREATE INDEX return_requests_customer_idx ON return_requests(customer_id, created_at DESC);

CREATE TABLE return_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    return_request_id uuid NOT NULL REFERENCES return_requests(id) ON DELETE CASCADE,
    order_item_id uuid NOT NULL REFERENCES order_items(id) ON DELETE RESTRICT,
    quantity integer NOT NULL CHECK (quantity > 0),
    condition_note text NOT NULL DEFAULT '',
    restock boolean NOT NULL DEFAULT false,
    UNIQUE(return_request_id, order_item_id)
);
CREATE INDEX return_items_order_item_idx ON return_items(order_item_id);
