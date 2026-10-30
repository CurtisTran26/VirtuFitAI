from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.admin.orders import OrderRefundRequest, OrderRefundResponse
from app.services.admin.orders import refund_and_restock_order
from app.services.orders.expiration import run_expiration_batch

v1 = "/api/v1"
router = APIRouter(prefix=f"{v1}/admin/orders", tags=["Admin Orders"])


@router.post("/{order_id}/refund", response_model=OrderRefundResponse)
def refund_order(
    order_id: UUID,
    payload: OrderRefundRequest,
    admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    """Hoàn tiền đơn hàng đã thanh toán và tự động hoàn trả tồn kho sản phẩm (chỉ dành cho Admin)."""
    return refund_and_restock_order(
        db,
        order_id=order_id,
        admin_id=admin["id"],
        payload=payload,
    )


@router.post("/expire-stale")
def trigger_expire_stale_orders(
    limit: int = Query(default=100, ge=1, le=500),
    admin=Depends(require_roles("admin", "warehouse_staff")),
    db: Session = Depends(get_db),
):
    """Kích hoạt thủ công job quét và hủy các đơn hàng quá hạn giữ chỗ 15 phút (Role: admin, warehouse_staff)."""
    result = run_expiration_batch(db, limit=limit)
    return {
        "status": "success",
        "expired_orders": result["expired_count"],
        "message": f"Đã hủy và giải phóng giữ chỗ cho {result['expired_count']} đơn hàng quá hạn.",
    }
