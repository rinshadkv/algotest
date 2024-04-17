from typing import List

from fastapi import FastAPI, WebSocket

app = FastAPI()

# Store all active connections
trades_socket_connections: List[WebSocket] = []
orders_socket_connections: List[WebSocket] = []


# WebSocket endpoint to accept messages and broadcast to all connections
@app.websocket("/trades")
async def trades_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    trades_socket_connections.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            # Broadcast received message to all connections
            for connection in trades_socket_connections:
                await connection.send_text(message)
    finally:
        trades_socket_connections.remove(websocket)


@app.websocket("/order-books")
async def order_book_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    orders_socket_connections.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            # Broadcast received message to all connections
            for connection in orders_socket_connections:
                await connection.send_text(message)
    finally:
        orders_socket_connections.remove(websocket)
