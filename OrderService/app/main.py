from fastapi import FastAPI, Depends

from . import models, crud
from .crud import *
from .database import *
from .rabbitmq import *

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/orders/")
async def place_order(order: schema.OrderBase, db: Session = Depends(get_db)):
    result = crud.create_order(db, order)
    publish_order(result, "create")
    return result.id


@app.get("/orders/{order_id}")
async def fetch_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)


@app.get("/orders/")
async def fetch_all_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)


@app.put("/orders/{order_id}")
async def update_order(order_id: int, order: schema.OrderPut, db: Session = Depends(get_db)):
    result = crud.modify_order(db, order_id, order)
    publish_order(result, "update")
    return {"success": True}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    # Get the order from the database to determine its side
    order = crud.get_order(db, order_id)
    if not order:
        return {"success": False}  # Order not found

    result = cancel_order(db, order_id)
    publish_order(result, "delete")
    return {"success": True}


@app.get("/trades/")
async def get_all_trades(db: Session = Depends(get_db)):
    return crud.get_all_trades(db)


@app.post("/trades/")
async def create_trade(trade: schema.Trade, db: Session = Depends(get_db)):
    return crud.create_trade(db, trade)


@app.get('/open-orders/')
async def get_open_orders(db: Session = Depends(get_db)):
    return crud.get_open_orders(db)


@app.on_event("startup")
async def startup_event():
    """
    add fake users to db.
    """
    add_fake_users()
