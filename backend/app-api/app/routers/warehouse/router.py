from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.warehouse.warehouse import (
    WarehouseOrderListResponse,
    WarehouseStatusUpdateRequest,
    WarehouseStatusUpdateResponse,
)
from app.services.warehouse.service import (
    list_warehouse_orders,
    update_fulfillment_status,
)

v1 = "/api/v1"
router = APIRouter(prefix=f"{v1}/warehouse/orders", tags=["Warehouse & Fulfillment"])


@router.get("", response_model=WarehouseOrderListResponse)
def get_orders(
    status: str | None = Query(default=None, description="Lọc theo trạng thái đơn hàng (ví dụ: confirmed, processing, ready_to_ship, shipped)"),
    order_type: str | None = Query(default=None, description="Lọc theo loại đơn (online, counter)"),
    order_date: date | None = Query(default=None, alias="date", description="Lọc theo ngày đặt hàng (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    staff=Depends(require_roles("warehouse_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Lấy danh sách đơn hàng cần chuẩn bị đóng gói và giao nhận cho kho (warehouse_staff, admin)."""
    return list_warehouse_orders(
        db,
        status=status,
        order_type=order_type,
        date_filter=order_date,
        page=page,
        limit=limit,
    )


@router.patch("/{order_id}/status", response_model=WarehouseStatusUpdateResponse)
def update_status(
    order_id: UUID,
    payload: WarehouseStatusUpdateRequest,
    staff=Depends(require_roles("warehouse_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Chuyển trạng thái quy trình đóng gói & giao nhận (confirmed -> processing -> ready_to_ship -> shipped -> completed)."""
    return update_fulfillment_status(
        db,
        order_id=order_id,
        staff_id=staff["id"],
        payload=payload,
    )

