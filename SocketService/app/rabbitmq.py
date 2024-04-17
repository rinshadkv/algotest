# import json
# import logging
# import time
#
# import pika
#
# from .websocket import broadcast_order_book_snapshot
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# MAX_RETRIES = 10
# RETRY_DELAY = 5
#
#
# def consume_updates():
#     connection = None
#     retry_count = 0
#     while retry_count < MAX_RETRIES:
#         try:
#             connection = pika.BlockingConnection(
#                 pika.ConnectionParameters('rabbitmq_server'))
#             break
#         except pika.exceptions.AMQPConnectionError:
#             logger.warning("Failed to connect to RabbitMQ. Retrying...")
#             time.sleep(RETRY_DELAY)
#             retry_count += 1
#
#     if not connection:
#         logger.error(
#             "Failed to connect to RabbitMQ after multiple retries. Exiting.")
#         return
#
#     channel = connection.channel()
#
#     # Declare exchange for trade messages
#     # channel.exchange_declare(exchange='trade', exchange_type='direct')
#     channel.exchange_declare(exchange='order_book_exchange', exchange_type='direct')
#
#     # Declare queues and bindings for trade updates and order book snapshots
#     # channel.queue_declare(queue='trade_snapshot')
#     # channel.queue_bind(exchange='trade', queue='trade_snapshot', routing_key='trade.snapshot')
#     channel.queue_declare(queue='order_book_snapshots')
#     channel.queue_bind(exchange='order_book_exchange', queue='order_book_snapshots', routing_key='order_book.snapshot')
#
#     def callback(ch, method, properties, body):
#         print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#         logger.info(body.decode())
#
#         # Handle trade updates or order book snapshots
#         if method.routing_key == 'order_book.snapshot':
#             logger.info(body.decode() + " order")
#             print("##############################")
#             # handle_order_book_snapshot(connected_clients, body.decode())
#
#     # Start consuming messages
#     # channel.basic_consume(queue='trade_snapshot', on_message_callback=callback, auto_ack=True)
#     channel.basic_consume(queue='order_book_snapshots', on_message_callback=callback, auto_ack=True)
#     channel.start_consuming()
#
#
# async def handle_order_book_snapshot(connected_clients, body):
#     """
#     Asynchronously handles the order book snapshot message and sends it to all connected WebSocket clients.
#     """
#     # Broadcast the order book snapshot data to all connected WebSocket clients
#     await broadcast_order_book_snapshot(connected_clients, json.loads(body))
