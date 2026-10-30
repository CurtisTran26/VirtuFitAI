from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class OrderItemDetail(BaseModel):
    id: UUID
    product_id: UUID
    variant_id: UUID
    product_name_snapshot: str
    sku_snapshot: str
    size_snapshot: str
    color_snapshot: str
    unit_price_vnd: int
    quantity: int
    line_total_vnd: int


class WarehouseOrderListItem(BaseModel):
    id: UUID
    order_number: str
    order_type: str
    status: str
    payment_method: str
    payment_status: str
    total_vnd: int
    address_snapshot: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemDetail] = []


class WarehouseOrderListResponse(BaseModel):
    items: list[WarehouseOrderListItem]
    total: int
    page: int
    limit: int


class WarehouseStatusUpdateRequest(BaseModel):
    next_status: Literal["processing", "ready_to_ship", "shipped", "completed"]
    carrier_name: str | None = Field(default=None, description="Đơn vị vận chuyển (GHN, GHTK, ViettelPost...)")
    tracking_code: str | None = Field(default=None, description="Mã vận đơn giao hàng")
    note: str | None = Field(default=None, max_length=500, description="Ghi chú đóng gói / giao hàng")

    @model_validator(mode="after")
    def validate_shipped_fields(self):
        if self.next_status == "shipped":
            if not self.carrier_name or not self.carrier_name.strip():
                raise ValueError("Đơn vị vận chuyển (carrier_name) là bắt buộc khi chuyển trạng thái sang shipped.")
            if not self.tracking_code or not self.tracking_code.strip():
                raise ValueError("Mã vận đơn (tracking_code) là bắt buộc khi chuyển trạng thái sang shipped.")
        return self


class WarehouseStatusUpdateResponse(BaseModel):
    order_id: UUID
    order_number: str
    from_status: str
    to_status: str
    carrier_name: str | None = None
    tracking_code: str | None = None
    changed_by: UUID
    updated_at: datetime
    message: str

