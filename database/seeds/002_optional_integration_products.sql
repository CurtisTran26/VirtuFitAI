-- OPTIONAL FIXTURES ONLY. Stored in PostgreSQL, not hardcoded in the mobile app.
-- Not real shop inventory. Prefix prevents collisions with existing catalog.
INSERT INTO categories(id,name) VALUES('10000000-0000-4000-8000-000000000001','Kiểm thử tích hợp') ON CONFLICT DO NOTHING;
INSERT INTO products(id,category_id,name,description,price_vnd,sku) VALUES
('20000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000001','Áo thun kiểm thử','Dữ liệu kiểm thử tích hợp, thay bằng hàng thực tế của nhóm.',189000,'S1-TEST-001'),
('20000000-0000-4000-8000-000000000002','10000000-0000-4000-8000-000000000001','Áo khoác kiểm thử hết hàng','Dữ liệu kiểm thử trạng thái hết hàng.',450000,'S1-TEST-002')
ON CONFLICT DO NOTHING;
INSERT INTO product_variants(id,product_id,size,color,sku,stock_on_hand) VALUES
('30000000-0000-4000-8000-000000000001','20000000-0000-4000-8000-000000000001','M','Đen','S1-TEST-001-M-D',5),
('30000000-0000-4000-8000-000000000002','20000000-0000-4000-8000-000000000001','L','Đen','S1-TEST-001-L-D',0),
('30000000-0000-4000-8000-000000000003','20000000-0000-4000-8000-000000000002','M','Nâu','S1-TEST-002-M-N',0)
ON CONFLICT DO NOTHING;
