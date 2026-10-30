from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail


def collect_cod_payment(
    db: Session,
    order_id: UUID,
    staff_id: UUID,
    staff_name: str = "",
) -> dict[str, Any]:
    """Xác nhận đối soát tiền COD cho đơn hàng."""
    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_method, payment_status
               FROM orders WHERE id = :id FOR UPDATE"""),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    if order["payment_method"] != "cod":
        fail(400, "INVALID_PAYMENT_METHOD", "Đơn hàng không sử dụng phương thức thanh toán COD.")

    if order["payment_status"] == "paid":
        fail(409, "ORDER_ALREADY_PAID", "Đơn hàng COD này đã được thu tiền và đối soát trước đó.")

    # Kiểm tra trạng thái hợp lệ: bắt buộc phải ở trạng thái shipped hoặc completed
    if order["status"] not in ("shipped", "completed"):
        fail(
            400,
            "INVALID_ORDER_STATE",
            f"Chỉ có thể thu tiền COD khi đơn hàng đang giao ('shipped') hoặc đã giao ('completed'). Trạng thái hiện tại: '{order['status']}'."
        )

    db.execute(
        text("""UPDATE orders
               SET payment_status = 'paid',
                   updated_at = now()
               WHERE id = :id"""),
        {"id": order["id"]}
    )

    staff_label = f" ({staff_name})" if staff_name else ""
    note = f"Đối soát thu tiền COD thành công: {order['total_vnd']:,} VND bởi nhân viên{staff_label}"

    db.execute(
        text("""INSERT INTO order_status_history(order_id, changed_by, from_status, to_status, note)
               VALUES(:order_id, :staff_id, :status, :status, :note)"""),
        {
            "order_id": order["id"],
            "staff_id": staff_id,
            "status": order["status"],
            "note": note,
        }
    )
    db.commit()

    return {
        "order_id": order["id"],
        "order_number": order["order_number"],
        "total_vnd": order["total_vnd"],
        "payment_method": order["payment_method"],
        "payment_status": "paid",
        "status": order["status"],
        "collector_id": staff_id,
        "message": f"Đối soát thu tiền COD thành công: {order['total_vnd']:,} VND.",
    }

