import asyncio
import json

from fastapi import FastAPI, WebSocket

from .rabbitmq import logger

app = FastAPI()

trade_ws_connections = set()
snapshot_ws_connections = set()


@app.websocket("/trade_ws")
async def websocket_trade_endpoint(websocket: WebSocket):
    await websocket.accept()
    trade_ws_connections.add(websocket)  # Add WebSocket connection to the set
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        trade_ws_connections.remove(websocket)  # Remove WebSocket connection from the set


@app.websocket("/snapshot_ws")
async def websocket_snapshot_endpoint(websocket: WebSocket):
    await websocket.accept()
    snapshot_ws_connections.add(websocket)  # Add WebSocket connection to the set
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        snapshot_ws_connections.remove(websocket)  # Remove WebSocket connection from the set


async def send_data_to_connections(data, connections):
    if connections:
        # Convert the data to JSON string
        message = json.dumps(data)
        # Send the message to all WebSocket connections
        await asyncio.gather(*[connection.send_text(message) for connection in connections])


async def handle_trade_update(body):
    # Handle trade update message
    trade_data = json.loads(body)
    # Process the trade data as needed
    logger.info(f"Received trade update: {trade_data}")

    # Send the trade data to all WebSocket connections for trade updates
    await send_data_to_connections(trade_data, trade_ws_connections)


async def handle_order_book_snapshot(body):
    # Handle order book snapshot message
    snapshot_data = json.loads(body)
    # Process the order book snapshot data as needed
    logger.info(f"Received order book snapshot: {snapshot_data}")
    # Send the snapshot data to all WebSocket connections for order book snapshots
    await send_data_to_connections(snapshot_data, snapshot_ws_connections)
