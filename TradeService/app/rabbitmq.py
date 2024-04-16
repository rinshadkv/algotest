import json
import time

import pika

from .order_book import *
from .schema import Order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 10
RETRY_DELAY = 5


def consume_orders():
    connection = None
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('rabbitmq_server'))
            break
        except pika.exceptions.AMQPConnectionError:
            logger.warning("Failed to connect to RabbitMQ. Retrying...")
            time.sleep(RETRY_DELAY)
            retry_count += 1

    if not connection:
        logger.error(
            "Failed to connect to RabbitMQ after multiple retries. Exiting.")
        return

    channel = connection.channel()

    channel.exchange_declare(exchange='order', exchange_type='direct')

    create_result = channel.queue_declare('', exclusive=True)
    create_queue_name = create_result.method.queue
    channel.queue_bind(
        exchange='order', queue=create_queue_name, routing_key='order.create')

    # Declare a queue for order updates
    update_result = channel.queue_declare('', exclusive=True)
    update_queue_name = update_result.method.queue
    channel.queue_bind(
        exchange='order', queue=update_queue_name, routing_key='order.update')

    # Declare a queue for order deletions
    delete_result = channel.queue_declare('', exclusive=True)
    delete_queue_name = delete_result.method.queue
    channel.queue_bind(
        exchange='order', queue=delete_queue_name, routing_key='order.delete')

    def callback(ch, method, properties, body):
        order_data = json.loads(body)
        action = order_data.get('action')
        order = Order(**order_data.get('order'))
        print(action, order)

        if action == 'create':
            # Add order to the order book
            add_to_order_book(order)
        elif action == 'update':
            # update order from order book
            update_order_book(order)

        elif action == 'delete':
            # Remove existing order from order book
            remove_order(order)

    # Set up a consumers
    channel.basic_consume(queue=create_queue_name,
                          on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue=update_queue_name,
                          on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue=delete_queue_name,
                          on_message_callback=callback, auto_ack=True)

    # Start consuming messages
    channel.start_consuming()


# def publish_order_book_snapshot(snapshot):
#     """
#     Publishes the order book snapshot to the RabbitMQ channel.
#     """
#     try:
#         # Establish connection to RabbitMQ server
#         connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq_server'))
#         channel = connection.channel()
#
#         # Declare exchange for publishing messages
#         channel.exchange_declare(exchange='order_book_snapshots', exchange_type='direct')
#
#         # Publish the snapshot to the 'order.snapshot' queue
#         channel.basic_publish(exchange='order_book_exchange', routing_key='order_book.snapshot', body=snapshot)
#
#         logger.info("Order book snapshot published successfully.")
#     except Exception as e:
#         logger.error(f"Failed to publish order book snapshot: {e}")
#     finally:
#         # Close the connection
#         if connection:
#             connection.close()
