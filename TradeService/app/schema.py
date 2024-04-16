import datetime
from typing import Optional


class Order:
    def __init__(
            self,
            id: Optional[int],
            quantity: int,
            price: float,
            side: str,
            trader_id: Optional[int],
            timestamp: Optional[datetime.datetime] = None,
            status: Optional[str] = None,
            is_deleted: Optional[bool] = False,
            created_at: Optional[datetime.datetime] = None,
            deleted_at: Optional[datetime.datetime] = None,
            updated_at: Optional[datetime.datetime] = None,
            traded_quantity: Optional[int] = None,
    ):
        self.id = id
        self.quantity = quantity
        self.price = price
        self.side = side
        self.trader_id = trader_id
        self.timestamp = timestamp
        self.status = status
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.deleted_at = deleted_at
        self.updated_at = updated_at
        self.traded_quantity = traded_quantity
