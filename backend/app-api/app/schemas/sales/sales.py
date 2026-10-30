from __future__ import annotations

from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field


class OrderItemInput(BaseModel):
    variant_id: UUID
    quantity: int = Field(default=1, ge=1, le=100, description="Số lượng sản phẩm")


class CounterOrderCreate(BaseModel):
    items: list[OrderItemInput] = Field(min_length=1, max_length=50, description="Danh sách sản phẩm")
    customer_id: UUID | None = Field(default=None, description="ID khách hàng thành viên (để None nếu khách vãng lai)")
    payment_method: Literal["cash", "bank_transfer", "card"] = Field(default="cash", description="Phương thức thanh toán tại quầy")
    note: str | None = Field(default=None, max_length=500, description="Ghi chú đơn hàng tại quầy")


class CashPaymentRequest(BaseModel):
    cash_received: int = Field(ge=0, description="Số tiền mặt khách đưa (VND)")


class CashPaymentResponse(BaseModel):
    order_id: UUID
    order_number: str
    total_vnd: int
    cash_received: int
    cash_change: int
    status: str
    payment_status: str
    staff_id: UUID
    message: str


class VietQRResponse(BaseModel):
    order_id: UUID
    order_number: str
    bank_id: str
    bank_name: str
    account_no: str
    account_name: str
    amount_vnd: int
    transfer_content: str
    qr_image_url: str
    emvco_payload: str


class TransferConfirmResponse(BaseModel):
    order_id: UUID
    order_number: str
    total_vnd: int
    status: str
    payment_status: str
    payment_method: str
    staff_id: UUID
    message: str

