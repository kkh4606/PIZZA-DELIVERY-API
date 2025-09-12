from pydantic import BaseModel
from typing import Optional


class Order(BaseModel):
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "SMALL"

    class Config:
        from_attributes = True


class UpdateOrderStatus(BaseModel):
    order_status: Optional[str] = "PENDING"
