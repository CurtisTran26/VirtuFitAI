from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.sales.sales import (
    CounterOrderCreate,
    CashPaymentRequest,
    CashPaymentResponse,
    VietQRResponse,
    TransferConfirmResponse,
)
from app.services.sales.service import (
    create_counter_order,
    pay_order_cash,
    generate_vietqr_payload,
    confirm_bank_transfer,
)

v1 = "/api/v1"
router = APIRouter(prefix=f"{v1}/sales/orders", tags=["Sales (POS & Quầy)"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order_at_counter(
    payload: CounterOrderCreate,
    staff=Depends(require_roles("sales_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Tạo đơn hàng bán trực tiếp tại quầy (dành cho sales_staff và admin)."""
    return create_counter_order(db, staff_id=staff["id"], payload=payload)


@router.post("/{order_id}/pay-cash", response_model=CashPaymentResponse)
def pay_cash(
    order_id: UUID,
    payload: CashPaymentRequest,
    staff=Depends(require_roles("sales_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Thanh toán tiền mặt tại quầy, tính tiền thừa và tự động khấu trừ kho."""
    return pay_order_cash(
        db,
        order_id=order_id,
        staff_id=staff["id"],
        cash_received=payload.cash_received,
    )


@router.post("/{order_id}/vietqr", response_model=VietQRResponse)
def get_vietqr(
    order_id: UUID,
    staff=Depends(require_roles("sales_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Sinh mã QR chuyển khoản VietQR Napas 247 cho đơn hàng tại quầy."""
    return generate_vietqr_payload(db, order_id=order_id)


@router.post("/{order_id}/confirm-transfer", response_model=TransferConfirmResponse)
def confirm_transfer(
    order_id: UUID,
    staff=Depends(require_roles("sales_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Nhân viên quầy xác nhận đã nhận được tiền chuyển khoản ngân hàng."""
    return confirm_bank_transfer(db, order_id=order_id, staff_id=staff["id"])

