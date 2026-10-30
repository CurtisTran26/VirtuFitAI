from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field


class VNPayCreateUrlRequest(BaseModel):
    order_id: UUID
    bank_code: str | None = Field(default=None, description="Mã ngân hàng thanh toán (tùy chọn: NCB, VCB, VISA,...)")


class VNPayCreateUrlResponse(BaseModel):
    payment_url: str
    order_id: UUID
    order_number: str
    amount_vnd: int


class VNPayIpnResponse(BaseModel):
    RspCode: str
    Message: str


class VNPayReturnResponse(BaseModel):
    is_success: bool
    order_number: str
    amount_vnd: int
    transaction_no: str | None = None
    response_code: str
    message: str


class VNPayReconciliationResponse(BaseModel):
    scanned_orders: int
    processed_orders: int
    confirmed_orders: int
    skipped_orders: int
    message: str
