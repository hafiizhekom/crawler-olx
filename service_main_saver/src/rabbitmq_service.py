import pika
import time
import json
from sqlite_service import SQLiteService 

class RabbitMQConsumer:
    def __init__(self, host='rabbitmq_python', port=5672, username='guest', password='guest', queue_name='store_head'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ server."""
        while True:
            try:
                print("Trying to connect to RabbitMQ...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=pika.PlainCredentials(self.username, self.password)
                    )
                )
                print("Connected to RabbitMQ!")
                self.channel = self.connection.channel()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}")
                time.sleep(5)

    def declare_queue(self):
        """Declare the queue to consume messages from."""
        if not self.channel:
            raise ValueError("Channel is not initialized. Connect to RabbitMQ first.")
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def start_consuming(self, sqlite_service):
        """Start consuming messages from the queue."""
        if not self.channel:
            raise ValueError("Channel is not initialized. Connect to RabbitMQ first.")

        def callback(ch, method, properties, body):
            message = body.decode()
            car = json.loads(message)
            print(f" [x] Received {car}")
            sqlite_service.save_message(car)

        sqlite_service.connect()
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=True
        )
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n [x] Stopping consumer...")
            self.close_connection()
            sqlite_service.close_connection()

    def close_connection(self):
        """Close the connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("RabbitMQ connection closed.")