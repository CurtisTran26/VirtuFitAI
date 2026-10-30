from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.payments.vnpay import (
    VNPayCreateUrlRequest,
    VNPayCreateUrlResponse,
    VNPayIpnResponse,
    VNPayReturnResponse,
    VNPayReconciliationResponse,
)
from app.services.payments.vnpay import (
    create_vnpay_payment_url,
    process_vnpay_ipn,
    process_vnpay_return,
)
from app.services.payments.reconciliation import run_reconciliation_batch

v1 = "/api/v1"
router = APIRouter(tags=["Payments"])


@router.post(f"{v1}/payments/vnpay/create-url", response_model=VNPayCreateUrlResponse)
def create_url(
    body: VNPayCreateUrlRequest,
    request: Request,
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Sinh URL thanh toán VNPay Sandbox phiên bản 2.1.0."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    return create_vnpay_payment_url(
        db,
        order_id=body.order_id,
        customer_id=user["id"],
        client_ip=client_ip,
        bank_code=body.bank_code,
    )


@router.get(f"{v1}/payments/vnpay/ipn", response_model=VNPayIpnResponse)
def vnpay_ipn(
    request: Request,
    db: Session = Depends(get_db),
):
    """Webhook Server-to-Server tiếp nhận kết quả thanh toán ngầm từ máy chủ VNPay."""
    params = dict(request.query_params)
    return process_vnpay_ipn(db, params)


@router.get(f"{v1}/payments/vnpay/return", response_model=VNPayReturnResponse)
def vnpay_return(
    request: Request,
):
    """Tiếp nhận chuyển hướng trình duyệt của người dùng sau khi hoàn tất giao dịch trên cổng VNPay."""
    params = dict(request.query_params)
    return process_vnpay_return(params)


@router.post(f"{v1}/payments/vnpay/reconcile", response_model=VNPayReconciliationResponse)
def reconcile_vnpay(
    lookback_minutes: int = Query(default=10, ge=1, le=1440, description="Số phút chờ tối thiểu để quét đơn VNPay treo"),
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(require_roles("warehouse_staff", "sales_staff", "admin")),
    db: Session = Depends(get_db),
):
    """Kích hoạt đối soát giao dịch định kỳ với VNPay QueryDR (warehouse_staff, sales_staff, admin)."""
    res = run_reconciliation_batch(db, lookback_minutes=lookback_minutes, limit=limit)
    return {
        "scanned_orders": res["scanned_orders"],
        "processed_orders": res["processed_orders"],
        "confirmed_orders": res["confirmed_orders"],
        "skipped_orders": res["skipped_orders"],
        "message": f"Đối soát hoàn tất: Đã quét {res['scanned_orders']} đơn, xác nhận thành công {res['confirmed_orders']} đơn.",
    }
