import logging
from collections import defaultdict
from heapq import heappush, heappop

from .crud import create_trade, fetch_orders_from_api
from .schema import *

# Priority queues for buy and sell orders
buy_order_book = defaultdict(list)
sell_order_book = defaultdict(list)

# Dictionary for order lookup (hash table)
orders = {}

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_order(order):
    if order.id in orders:
        existing_order = orders[order.id]
        del orders[order.id]
        if order.side == "BUY":
            heappop(buy_order_book[existing_order.price])
        elif order.side == "SELL":

            heappop(sell_order_book[existing_order.price])


def update_order_book(order):
    remove_order(order)
    add_to_order_book(order)


def add_to_order_book(order):
    # Add order to the hash table
    orders[order.id] = order

    # Add order to the appropriate side (buy or sell) and price level with timestamp as priority
    if order.side == "BUY":
        heappush(buy_order_book[order.price], (order.timestamp, order))
    elif order.side == "SELL":
        heappush(sell_order_book[order.price], (order.timestamp, order))
    match_and_create_trades(order)


def match_and_create_trades(order):
    if order.side == "BUY":
        logger.info(f"Matching buy order: {order}")
        # Iterate through sell orders sorted by price (ascending)
        for price, sell_orders in sorted(sell_order_book.items()):
            for _, sell_order in sell_orders:
                if sell_order.price <= order.price:  # Check price priority and limit
                    if order.quantity >= sell_order.quantity:
                        logger.info("Creating trade...")
                        create_trade(order, sell_order)
                        del orders[sell_order.id]
                        heappop(sell_order_book[price])  # Remove matched order
                        order.quantity -= sell_order.quantity
                        # Remove the fully consumed buy order
                        if order.quantity == 0:
                            del orders[order.id]
                            heappop(buy_order_book[price])  # Remove matched order
                        break  # Exit inner loop after successful match
                    else:
                        logger.info("Creating partial trade...")
                        create_trade(order, sell_order)
                        # Update order quantities
                        order.quantity -= sell_order.quantity
                        sell_order.quantity -= order.quantity
                        # Remove the fully consumed sell order
                        if sell_order.quantity == 0:
                            del orders[sell_order.id]
                            heappop(sell_order_book[price])
                        # Remove the fully consumed buy order
                        if order.quantity == 0:
                            del orders[order.id]
                            heappop(buy_order_book[price])
                        break  # Exit inner loop after partial match
                else:
                    break
            # Exit outer loop if order is fully filled
            if order.quantity == 0:
                break

    elif order.side == "SELL":
        logger.info(f"Matching sell order: {order}")
        # Iterate through buy orders sorted by price (descending) - reverse sort for highest bid
        for price, buy_orders in sorted(buy_order_book.items(), reverse=True):
            for _, buy_order in buy_orders:
                if buy_order.price >= order.price:  # Check price priority and limit
                    if order.quantity >= buy_order.quantity:
                        logger.info("Creating trade...")
                        create_trade(buy_order, order)
                        del orders[buy_order.id]
                        heappop(buy_order_book[price])  # Remove matched order
                        order.quantity -= buy_order.quantity
                        if order.quantity == 0:
                            del orders[order.id]
                            heappop(sell_order_book[price])
                        break  # Exit inner loop after successful match
                    else:
                        logger.info("Creating partial trade...")
                        create_trade(buy_order, order)
                        # Trade with full buy order quantity
                        buy_order.quantity -= order.quantity
                        # Remove the fully consumed buy order
                        del orders[order.id]
                        heappop(sell_order_book[price])
                        # remove the buy order if it is filled
                        if buy_order.quantity == 0:
                            del orders[buy_order.id]
                            heappop(buy_order_book[price])
                        break  # Exit inner loop after partial match
            # Exit outer loop if order is fully filled
            if order.quantity == 0:
                break


def populate_data_structures():
    """
    Populate the data structures with orders data fetched from the API.
    """
    # Fetch orders data from the API
    orders_data = fetch_orders_from_api()

    if orders_data:
        # Populate the orders dictionary
        for order_data in orders_data:
            order = Order(**order_data)  # Create Order instance from dictionary
            orders[order.id] = order

        # Clear existing data in order books
        buy_order_book.clear()
        sell_order_book.clear()

        # Populate order books
        for order in orders.values():
            add_to_order_book(order)
