import pika
import time

class RabbitMQService:
    def __init__(self, host='rabbitmq_python', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Mencoba untuk koneksi ke RabbitMQ"""
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

    def send_message(self, queue_name, message):
        try:
            if not self.channel or self.connection.is_closed:
                print("Reconnecting to RabbitMQ...")
                self.connect()
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
            print(f" [x] Sent '{message}' to queue '{queue_name}'")
        except Exception as e:
            print(f"Failed to send message to queue '{queue_name}': {e}")

    def close_connection(self):
        """Menutup koneksi ke RabbitMQ"""
        if self.connection:
            self.connection.close()
            print("Connection closed.")
        else:
            print("No active connection to close.")