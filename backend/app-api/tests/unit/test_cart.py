from __future__ import annotations

import unittest
from uuid import UUID
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from shared_platform import SessionLocal, current_user


class CartApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.user_id = UUID("698cc9c6-1238-4088-8fc4-104eec02af88")
        self.test_user = {
            "id": self.user_id,
            "phone": "0912345678",
            "full_name": "Nguyen Van A",
            "is_active": True,
            "role": "customer",
        }
        # Override authentication dependency
        app.dependency_overrides[current_user] = lambda: self.test_user

        # Clear cart for test user
        self.db.execute(text("DELETE FROM cart_items WHERE user_id = :u"), {"u": self.user_id})
        self.db.commit()

        # Known seeded variants
        # Variant 1: stock = 5, reserved = 0 (Product active = true)
        self.valid_variant_id = UUID("30000000-0000-4000-8000-000000000001")
        # Variant 2: stock = 0, reserved = 0
        self.out_of_stock_variant_id = UUID("30000000-0000-4000-8000-000000000002")

        # Ensure product for valid variant is active
        self.db.execute(
            text("UPDATE products SET is_active = true WHERE id = (SELECT product_id FROM product_variants WHERE id = :v)"),
            {"v": self.valid_variant_id}
        )
        self.db.commit()

    def tearDown(self):
        # Clean up cart items after test
        self.db.execute(text("DELETE FROM cart_items WHERE user_id = :u"), {"u": self.user_id})
        # Reset is_active for seeded products
        self.db.execute(
            text("UPDATE products SET is_active = true WHERE id = (SELECT product_id FROM product_variants WHERE id = :v)"),
            {"v": self.valid_variant_id}
        )
        self.db.commit()
        self.db.close()
        app.dependency_overrides.clear()

    def test_01_add_valid_variant_to_cart_success(self):
        """1. Test thêm biến thể hợp lệ vào giỏ hàng -> Trả về 201 Created."""
        payload = {
            "variant_id": str(self.valid_variant_id),
            "quantity": 2
        }
        res = self.client.post("/api/v1/cart/items", json=payload)
        self.assertEqual(res.status_code, 201, res.text)
        data = res.json()
        self.assertEqual(data["total_items"], 2)
        self.assertEqual(data["total_unique_items"], 1)
        self.assertEqual(len(data["items"]), 1)
        
        item = data["items"][0]
        self.assertEqual(item["variant_id"], str(self.valid_variant_id))
        self.assertEqual(item["quantity"], 2)
        self.assertTrue(item["is_available"])
        self.assertIsNone(item["unavailable_reason"])
        self.assertEqual(data["subtotal_vnd"], item["price_vnd"] * 2)

    def test_02_upsert_accumulate_quantity(self):
        """2. Test thêm biến thể đã có sẵn trong giỏ -> Số lượng được cộng dồn chính xác."""
        # Lần 1: Thêm 1 sản phẩm
        res1 = self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 1}
        )
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res1.json()["total_items"], 1)

        # Lần 2: Thêm tiếp 2 sản phẩm cùng variant
        res2 = self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 2}
        )
        self.assertEqual(res2.status_code, 201)
        data = res2.json()
        self.assertEqual(data["total_items"], 3)
        self.assertEqual(data["total_unique_items"], 1)
        self.assertEqual(data["items"][0]["quantity"], 3)

    def test_03_add_variant_exceeding_stock_fails(self):
        """3. Test thêm biến thể với số lượng vượt quá tồn kho khả dụng -> Báo lỗi 409 Conflict."""
        # Variant 1 có tồn kho khả dụng = 5
        payload = {
            "variant_id": str(self.valid_variant_id),
            "quantity": 10  # vượt quá tồn kho 5
        }
        res = self.client.post("/api/v1/cart/items", json=payload)
        self.assertEqual(res.status_code, 409, res.text)
        data = res.json()
        self.assertEqual(data["error"]["code"], "OUT_OF_STOCK")

    def test_04_update_quantity_invalid(self):
        """4. Test cập nhật số lượng biến thể <= 0 -> Báo lỗi 422 Unprocessable Entity."""
        # Thêm 1 item vào giỏ trước
        self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 1}
        )

        # Cập nhật số lượng = 0
        res = self.client.patch(
            f"/api/v1/cart/items/{self.valid_variant_id}",
            json={"quantity": 0}
        )
        self.assertEqual(res.status_code, 422, res.text)
        data = res.json()
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

        # Cập nhật số lượng âm
        res_neg = self.client.patch(
            f"/api/v1/cart/items/{self.valid_variant_id}",
            json={"quantity": -5}
        )
        self.assertEqual(res_neg.status_code, 422)

    def test_05_inactive_product_marked_unavailable_in_cart(self):
        """5. Test sản phẩm cha bị ẩn (is_active = false) -> Báo không khả dụng khi lấy giỏ hàng."""
        # Thêm 1 item vào giỏ lúc sản phẩm còn active
        res_add = self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 1}
        )
        self.assertEqual(res_add.status_code, 201)

        # Đổi is_active của product thành false trong DB
        self.db.execute(
            text("UPDATE products SET is_active = false WHERE id = (SELECT product_id FROM product_variants WHERE id = :v)"),
            {"v": self.valid_variant_id}
        )
        self.db.commit()

        # Gọi GET /cart
        res_get = self.client.get("/api/v1/cart")
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json()
        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        self.assertFalse(item["is_available"])
        self.assertIn("ngừng kinh doanh", item["unavailable_reason"].lower())
        # Subtotal không tính các item không khả dụng
        self.assertEqual(data["subtotal_vnd"], 0)

    def test_06_delete_cart_item(self):
        """6. Test xóa một mục cụ thể khỏi giỏ hàng -> 204 No Content."""
        self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 1}
        )

        del_res = self.client.delete(f"/api/v1/cart/items/{self.valid_variant_id}")
        self.assertEqual(del_res.status_code, 204)

        get_res = self.client.get("/api/v1/cart")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["total_items"], 0)
        self.assertEqual(len(get_res.json()["items"]), 0)

    def test_07_clear_entire_cart(self):
        """7. Test xóa sạch toàn bộ giỏ hàng -> 204 No Content."""
        self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 2}
        )

        del_res = self.client.delete("/api/v1/cart")
        self.assertEqual(del_res.status_code, 204)

        get_res = self.client.get("/api/v1/cart")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["total_items"], 0)

    def test_08_update_valid_quantity_success(self):
        """8. Test cập nhật số lượng hợp lệ trong phạm vi tồn kho -> Trả về 200 OK với số lượng mới."""
        self.client.post(
            "/api/v1/cart/items",
            json={"variant_id": str(self.valid_variant_id), "quantity": 1}
        )

        patch_res = self.client.patch(
            f"/api/v1/cart/items/{self.valid_variant_id}",
            json={"quantity": 4}
        )
        self.assertEqual(patch_res.status_code, 200)
        data = patch_res.json()
        self.assertEqual(data["total_items"], 4)
        self.assertEqual(data["items"][0]["quantity"], 4)
        self.assertEqual(data["subtotal_vnd"], data["items"][0]["price_vnd"] * 4)


if __name__ == "__main__":
    unittest.main()
