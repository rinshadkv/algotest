# Introduction

The Order API is designed to facilitate trading activities by providing functionalities to place, modify, cancel, and
fetch orders on an exchange. It includes a matching engine that matches bid and ask orders to execute trades. This
documentation outlines the architecture, functionalities, endpoints, and data flow of the Order API.

## Architecture Overview

The Order API is implemented as a set of microservices, each responsible for specific functionalities:

* Order Service: Handles CRUD operations on orders and interacts with the database. Exposes public endpoints for order
  management.
* Trade Service: Manages order matching and maintains the order book. Receives messages from the Order Service for order
  updates and broadcasts orderbook snapshot periodically.
* Socket Service: Manages WebSocket connections for real-time broadcasting of order book snapshots and trade updates.

## Technologies Used

* FastAPI: Python-based web framework for building APIs.
* Docker: Containerization for deployment.
* PostgreSQL: Relational database for storing orders and trades.
* RabbitMQ: Message queuing system for communication between microservices.
* Websockets: Protocol for real-time communication with clients.

## Functionalities

* Place Order [POST]

  **Endpoint: /orders**

  Description: Places a new order on the exchange.
  Payload:
   ```
   Quantity (int, > 0)
    Price (float, > 0)
    Side (1 for buy, -1 for sell) 
  ```
  Returns: Order ID
* Modify Order [PUT]

  **Endpoint: /orders/{order_id}**

  Description: Modifies an existing order.
  Payload:

  ```
  Updated Price
  ```
  Returns: Success (bool)


* Cancel Order [DELETE]

  **Endpoint: /orders/{order_id}**

  Description: Cancels an existing order.
  Payload:
  ```
   Order ID
  ```
  Returns: Success (bool)
* Fetch Order [GET]

  **Endpoint: /orders/{order_id}**

  Description: Fetches details of a specific order.
  Payload:
  ```
  Order ID
  ```
  Returns:
  Order Price,
  Order Quantity
  Average Traded Price
  Traded Quantity
  Order Alive (bool)


* Get All Orders [GET]

  **Endpoint: /orders**

  Description: Fetches all placed orders.
  Returns: List of order details (similar to Fetch Order)
* Get All Trades [GET]

  **Endpoint: /trades**

  Description: Fetches all trades that have taken place.
  Returns: List of trade details

* Trades [WEBSOCKET]

   **Endpoint: ws://localhost:8080/trades**

   Description: Broadcast live trades


* OrderBook Snapshot [WEBSOCKET] 

   **Endpoint: ws://localhost:8080/order-books**

   Description: Broadcast live order book snapshots

## Microservices Overview

### Order Service

#### Responsibilities:

* CRUD operations on orders
* Database interaction
* Exposes public endpoints
* saving trades to database

#### Data Flow:

* Receives requests from clients
* Stores orders in the database
* Sends messages to Trade Service for order updates
* receive matching orders from trade service and saves to database then sends to socket service through rabbitmq for
  websocket communication

### Trade Service

#### Responsibilities:

* Order matching
* Maintains order book
    * Broadcasts order book snapshot through rabbitmq to socket service

#### Data Flow:

* Listens for messages from Order Service
* Matches orders and updates order book
* Sends matching orders order service through api for save to database

### Socket Service

#### Responsibilities:

* Manages WebSocket connections
* Broadcasts order book snapshots and trade updates

#### Data Flow:

* Receives trade updates from Trade Service
* Receives order book snapshots from Trade Service
* Broadcasts updates to WebSocket clients

#### Data Flow Diagram

![ezcv logo](https://i.postimg.cc/bryzzCpd/diagram.png)

### Deployment

##### Containerization: All services are containerized using Docker.

##### Docker Compose: Docker Compose file is provided for managing multi-container applications.

##### Instructions: Follow the README for instructions on how to build and run the application.

#### Testing

* Use the provided Postman collection to test the API functionalities.
* you can find a postman collection file in root directory 
* WebSocket connections can be tested using WebSocket client tools.
* Conclusion

The Order API provides a robust platform for managing orders and executing trades on the exchange. Its microservices
architecture ensures scalability and fault tolerance, while the use of modern technologies enables real-time
communication and efficient order matching.

# How to Run the Application

To run the Order API application, follow these steps:

1. Make sure you have Docker installed on your machine.

2. Clone the repository containing the Order API code.

```
git clone https://github.com/rinshadkv/algotest.git
```

3. Navigate to the root directory of the project.

```
cd /algotest
```

4. Open a terminal window.

5. Run the following command to build and start the Docker containers:

```
docker-compose up --build
```

This command will build the Docker images for each service and start the containers defined in the `docker-compose.yml`
file.

6. Once the containers are up and running, you can access the APIs provided by the Order Service on port 8000, WebSocket
   connections managed by the Socket Service on port 8080, and Trade updates from the Trade Service on port 9000.

- Order Service API: http://localhost:8000
- Socket Service WebSocket: ws://localhost:8080
- Trade Service: http://localhost:9000

7. You can also interact with the PostgreSQL database directly on port 5432 and with RabbitMQ on port 5672.

8. To stop the containers, press `Ctrl + C` in the terminal where they are running, and then run the following command
   to remove the containers:



