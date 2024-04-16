from fastapi import FastAPI

from .order_book import populate_data_structures
from .rabbitmq import consume_orders

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    Populate the data structures with orders data fetched from the API.
    """
    populate_data_structures()
    # Run the consume_orders function in a background task when the application starts
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.create_task(consume_orders())
