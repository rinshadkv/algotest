from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Side(Enum):
    BUY = 1
    SELL = -1


class Status(Enum):
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    PENDING = "PENDING"


class OrderBase(BaseModel):
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0, )
    side: Side
    trader_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True


class OrderPut(BaseModel):
    updated_price: float = Field(..., gt=0)


class Trade(BaseModel):
    price: float
    quantity: int
    buyer_order_id: int
    seller_order_id: int

    class Config:
        from_attributes = True


class OrderDTO(BaseModel):
    id: int
    order_price: float
    order_quantity: int
    average_traded_price: float
    traded_quantity: int
    order_alive: bool


class TradeDTO(BaseModel):
    id: int
    price: float
    quantity: int
    buyer_order_id: int
    seller_order_id: int
    execution_timestamp: datetime
    unique_id: str
