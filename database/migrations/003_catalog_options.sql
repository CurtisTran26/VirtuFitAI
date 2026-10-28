CREATE TABLE IF NOT EXISTS catalog_options (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    option_type text NOT NULL CHECK (option_type IN ('color', 'size')),
    name varchar(80) NOT NULL,
    hex_color varchar(7),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        (option_type = 'color' AND hex_color ~ '^#[0-9A-Fa-f]{6}$') OR
        (option_type = 'size' AND hex_color IS NULL)
    ),
    UNIQUE (option_type, name)
);
