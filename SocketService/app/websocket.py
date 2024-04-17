# import json
# import logging
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# async def broadcast_order_book_snapshot(connected_clients, snapshot_data):
#     for client in connected_clients:
#         try:
#             # Send the order book snapshot data as JSON to each connected client
#             await client.send_text(json.dumps(snapshot_data))
#             logger.info("Order book snapshot sent to WebSocket client successfully.")
#         except Exception as e:
#             logger.error(f"Failed to send order book snapshot to WebSocket client: {e}")
