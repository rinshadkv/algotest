import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_trade(buy_order, sell_order):
    """
    Creates a Trade object based on the buy and sell orders.
    """
    ORDER_SERVICE_URL = "http://order_service:8000/trades"

    trade_quantity = min(buy_order.quantity, sell_order.quantity)
    trade_price = sell_order.price  # sell order sets the price for the trade
    trade = {
        "price": trade_price,
        "quantity": trade_quantity,
        "buyer_order_id": buy_order.id,
        "seller_order_id": sell_order.id
    }

    response = requests.post(ORDER_SERVICE_URL, json=trade)
    if response.status_code == 201:
        return response.json()
    else:
        print(response)
        return None


def fetch_orders_from_api():
    """
    Fetch orders data from the API endpoint.
    """
    # Make a GET request to the /orders API endpoint
    response = requests.get("http://order_service:8000/open-orders")
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return JSON data
    else:
        print("Failed to fetch orders data from the API.")
        return None

# async def publish_order_book_snapshot(snapshot):
#     logger.info("Publishing order snapshot")
#     print(snapshot)
#     """
#     Publishes the order book snapshot to the WebSocket channel.
#     """
#     uri = "ws://localhost:8080/ws"
#     async with websockets.connect(uri) as websocket:
#         await websocket.send(snapshot)

# """
# Publishes the order book snapshot to the RabbitMQ channel.
# """
# try:
#     # Establish connection to RabbitMQ server
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters('rabbitmq_server'))
#     channel = connection.channel()
#
#     # Declare exchange for publishing messages
#     channel.exchange_declare(
#         exchange='order_book_exchange', exchange_type='direct')
#
#     # Publish the snapshot to the 'order.snapshot' queue
#     channel.basic_publish(exchange='order_book_exchange',
#                           routing_key='order_book.snapshot', body=snapshot)
#
#     logger.info("Order book snapshot published successfully.")
# except Exception as e:
#     logger.error(f"Failed to publish order book snapshot: {e}")
