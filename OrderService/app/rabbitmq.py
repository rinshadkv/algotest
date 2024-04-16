import json
import logging

import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def publish_order(order, action):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq_server'))

    """
    Publishes a new order to a RabbitMQ queue named "order" with routing key "order.create".

    Args:
        order: A dictionary representing the order details.
        action: A string indicating the action (create, update, delete).
    """

    # Establish connection to RabbitMQ server
    channel = connection.channel()

    # Declare the exchange (ideally in a separate function for reusability)
    channel.exchange_declare(exchange="order", exchange_type="direct")

    # Serialize the order to JSON with proper indentation
    order_json = json.dumps({"action": action, "order": order.to_dict()})  # Include action in message

    # Determine routing key based on action
    routing_key = f"order.{action}"  # Use different routing keys for different actions

    # Publish the order to the exchange with appropriate routing key
    channel.basic_publish(exchange="order", routing_key=routing_key,
                          body=order_json.encode())  # Encode for transmission

    # Close the connection
    connection.close()


def publish_trade(db_trade):
    """
    Publishes a new trade to a RabbitMQ queue named "trade" with routing key "trade.snapshot".
    """
    try:
        # Establish connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq_server'))
        channel = connection.channel()

        # Declare exchange for publishing messages
        channel.exchange_declare(exchange='trade', exchange_type='direct')

        # Publish the snapshot to the 'trade.snapshot' queue
        channel.basic_publish(exchange='trade', routing_key='trade.snapshot', body=db_trade)

        logger.info("Trade snapshot published successfully.")
    except Exception as e:
        logger.error(f"Failed to publish trade snapshot: {e}")
    finally:
        # Close the connection
        if connection:
            connection.close()
