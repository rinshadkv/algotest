import logging
import uuid

from fastapi import HTTPException
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from . import schema
from .database import SessionLocal
from .models import *
from .rabbitmq import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_order(db: Session, order: schema.OrderBase):
    db_order = Order(**order.model_dump(),
                     timestamp=dt.datetime.now(), status=Status.PENDING)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_orders(buyer_order_id, seller_order_id, quantity):
    session = SessionLocal()
    buyer_order = session.query(Order).filter(
        and_(Order.id == buyer_order_id, Order.is_deleted ==
             False, Order.status != Status.CANCELLED)
    ).first()
    seller_order = session.query(Order).filter(
        and_(Order.id == seller_order_id, Order.is_deleted ==
             False, Order.status != Status.CANCELLED)
    ).first()

    # Update the traded quantities for both orders
    buyer_order.traded_quantity += quantity
    seller_order.traded_quantity += quantity
    if buyer_order.traded_quantity == buyer_order.quantity:
        buyer_order.status = Status.FILLED
    else:
        buyer_order.status = Status.PARTIALLY_FILLED

    if seller_order.traded_quantity == seller_order.quantity:
        seller_order.status = Status.FILLED
    else:
        seller_order.status = Status.PARTIALLY_FILLED

    # Commit the changes to the database
    session.commit()


def create_trade(db: Session, trade: schema.Trade):
    # Generate a unique identifier for the trade
    unique_id = str(uuid.uuid4())

    # Create a new Trade object with the provided data
    db_trade = Trade(
        **trade.model_dump(),
        execution_timestamp=dt.datetime.now(),
        unique_id=unique_id  # Assign the unique identifier to the trade
    )

    # Add the trade to the database session
    db.add(db_trade)
    db.commit()

    # Refresh the trade object to get the updated attributes
    db.refresh(db_trade)

    # Update related orders
    update_orders(trade.buyer_order_id, trade.seller_order_id, trade.quantity)
    publish_trade(db_trade)

    # Return the ID of the created trade
    return db_trade.id


def get_order(db: Session, order_id: int):
    # Retrieve the order from the database
    db_order = db.query(Order).filter(
        and_(Order.id == order_id, Order.is_deleted ==
             False, Order.status != Status.CANCELLED)
    ).first()

    # Check if the order exists
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Calculate the average traded price
    average_traded_price = calculate_average_traded_price(db, db_order.id)

    # Check if the order is still active
    order_alive = db_order.status not in [Status.CANCELLED, Status.FILLED]

    # Create an OrderDTO object with the order details
    order_dto = OrderDTO(
        id=db_order.id,
        order_price=db_order.price,
        order_quantity=db_order.quantity,
        average_traded_price=average_traded_price,
        order_alive=order_alive,
        traded_quantity=db_order.traded_quantity,
    )
    return order_dto


def get_orders(db: Session):
    # Retrieve the orders from the database
    orders = db.query(Order).filter(
        and_(Order.is_deleted == False, Order.status != Status.CANCELLED)
    ).all()
    order_dtos = []
    for order in orders:
        # Calculate the average traded price
        average_traded_price = calculate_average_traded_price(db, order.id)
        order_alive = order.status not in [Status.CANCELLED, Status.FILLED]
        order_dto = OrderDTO(
            id=order.id,
            order_price=order.price,
            order_quantity=order.quantity,
            average_traded_price=average_traded_price,
            order_alive=order_alive,
            traded_quantity=order.traded_quantity,
        )
        order_dtos.append(order_dto)

    return order_dtos


def get_open_orders(db: Session):
    """
    Get open orders from the database.
    """
    return db.query(Order).filter(
        and_(
            Order.is_deleted == False,
            or_(
                Order.status == Status.PENDING,
                Order.status == Status.OPEN,
                Order.status == Status.PARTIALLY_FILLED
            )
        )
    ).all()


def modify_order(db: Session, order_id: int, order: schema.OrderPut):
    # Retrieve the order from the database
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status == Status.FILLED:
        raise HTTPException(
            status_code=400, detail="Cannot modify a filled order")
    # Update the order's price
    db_order.price = order.updated_price
    db.commit()
    return db_order


def cancel_order(db: Session, order_id: int):
    # Retrieve the order from the database
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        return False

    # Calculate total traded quantity for the order
    total_traded_quantity = db.query(func.sum(Trade.quantity)).filter(
        (Trade.buyer_order_id == order_id) | (
            Trade.seller_order_id == order_id)
    ).scalar() or 0

    if total_traded_quantity == 0:
        # Order has not been traded at all, delete it
        db_order.deleted_at = dt.datetime.now()
        db_order.status = Status.CANCELLED
        db_order.is_deleted = True
    else:
        # Update remaining quantity if order has been partially traded
        db_order.quantity -= total_traded_quantity
        db_order.deleted_at = dt.datetime.now()
        db_order.status = Status.CANCELLED
        db_order.is_deleted = True

    db.commit()
    return db_order


def add_fake_users():
    try:
        # Open a session
        session = SessionLocal()

        # Create fake users
        fake_users = [
            User(name='John Doe', email='john@example.com'),
            User(name='Jane Doe', email='jane@example.com'),
            User(name='Alice Smith', email='alice@example.com'),
            User(name='Bob Brown', email='bob@example.com'),
            User(name='Eve Johnson', email='eve@example.com'),

        ]

        # Add users to session
        for user in fake_users:
            session.add(user)

        # Commit the session to persist the changes to the database
        session.commit()

        # Close the session
        session.close()

        logger.info("Fake users added successfully")

    except Exception as e:
        logger.error("An error occurred while adding fake users: %s", e)


def calculate_average_traded_price(db: Session, order_id: int) -> float:
    # Retrieve all trades associated with the order
    trades = db.query(Trade).filter(
        (Trade.buyer_order_id == order_id) | (
            Trade.seller_order_id == order_id)
    ).all()

    # Calculate total traded value and quantity
    total_traded_value = sum(trade.price * trade.quantity for trade in trades)
    total_traded_quantity = sum(trade.quantity for trade in trades)

    # Calculate average traded price
    if total_traded_quantity != 0:
        average_price = total_traded_value / total_traded_quantity
        return round(average_price, 2)
    else:
        return 0.0


def get_all_trades(db):
    orders = db.query(Trade).filter(
        Order.is_deleted == False
    ).all()
    trade_dtos = []
    for trade in orders:
        trade_dto = TradeDTO(
            id=trade.id,
            price=trade.price,
            quantity=trade.quantity,
            buyer_order_id=trade.buyer_order_id,
            seller_order_id=trade.seller_order_id,
            execution_timestamp=trade.execution_timestamp,
            unique_id=trade.unique_id,
        )
        trade_dtos.append(trade_dto)

    return trade_dtos
