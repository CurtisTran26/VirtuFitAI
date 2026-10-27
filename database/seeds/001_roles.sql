INSERT INTO roles(name,description) VALUES
('customer','Customer account'),('sales_staff','Sales staff'),('warehouse_staff','Warehouse staff'),('designer','Designer'),('admin','Administrator')
ON CONFLICT(name) DO UPDATE SET description=EXCLUDED.description;
