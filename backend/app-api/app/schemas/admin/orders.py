from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class OrderRefundRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500, description="Lý do hoàn tiền đơn hàng")
    refund_amount: int | None = Field(default=None, ge=1, description="Số tiền hoàn lại (để trống để hoàn toàn bộ total_vnd)")


class RestockedItemDetail(BaseModel):
    variant_id: UUID
    quantity_restocked: int
    stock_before: int
    stock_after: int


class OrderRefundResponse(BaseModel):
    order_id: UUID
    order_number: str
    total_vnd: int
    refund_amount: int
    status: str
    payment_status: str
    refund_reason: str
    admin_id: UUID
    refunded_at: datetime
    restocked_items: list[RestockedItemDetail]
    message: str

