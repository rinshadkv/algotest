import datetime as dt

from sqlalchemy import Column, Integer, DateTime, Float, String, Enum as SQLAlchemyEnum, Boolean, ForeignKey, TIMESTAMP, \
    UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .schema import *

Base = declarative_base()


class BaseProperties(Base):
    __abstract__ = True
    created_at = Column(TIMESTAMP, default=dt.datetime.now())
    updated_at = Column(TIMESTAMP, default=dt.datetime.now())
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)


class Order(BaseProperties):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True,
                nullable=False, autoincrement=True)
    timestamp = Column(TIMESTAMP, default=dt.datetime.now(), index=True)
    quantity = Column(Integer)
    price = Column(Float, index=True)
    side = Column(SQLAlchemyEnum(Side, index=True))
    status = Column(SQLAlchemyEnum(Status))
    trader_id = Column(Integer, ForeignKey("users.id"))
    traded_quantity = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "quantity": self.quantity,
            "price": self.price,
            "side": self.side.name,
            "status": self.status.name,
            "trader_id": self.trader_id,
            "traded_quantity": self.traded_quantity
        }


class Trade(BaseProperties):
    __tablename__ = "trade"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    price = Column(Float)
    quantity = Column(Integer)
    buyer_order_id = Column(Integer, ForeignKey("orders.id"))
    seller_order_id = Column(Integer, ForeignKey("orders.id"))
    buyer_order = relationship("Order", foreign_keys=[
        buyer_order_id], backref="buyer_trades")
    seller_order = relationship("Order", foreign_keys=[
        seller_order_id], backref="seller_trades")
    execution_timestamp = Column(TIMESTAMP, default=dt.datetime.now())
    unique_id = Column(String(255))
    UniqueConstraint("unique_id", name="uix_1"),

    class Config:
        orm_mode = True


class User(BaseProperties):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,
                nullable=False, autoincrement=True)
    name = Column(String)
    email = Column(String)
