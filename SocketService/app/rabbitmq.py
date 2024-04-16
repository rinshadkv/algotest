import logging
import time

import pika

from .main import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 10
RETRY_DELAY = 5


def consume_updates():
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
        logger.error("Failed to connect to RabbitMQ after multiple retries. Exiting.")
        return

    channel = connection.channel()

    # Declare queues and bindings for trade updates and order book snapshots
    channel.queue_declare(queue='trade')
    channel.queue_bind(exchange='trade', queue='trade', routing_key='trade.snapshot')
    channel.queue_declare(queue='order_book_snapshots')
    channel.queue_bind(exchange='order_book', queue='order_book_snapshots', routing_key='order_book.snapshot')

    def callback(ch, method, properties, body):
        # Handle trade updates or order book snapshots
        if method.routing_key == 'trade.snapshot':
             handle_trade_update(body)
        elif method.routing_key == 'order_book.snapshot':
            handle_order_book_snapshot(body)

    # Start consuming messages
    channel.basic_consume(queue='trade_snapshot', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='order_book_snapshots', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
