import pika
import time

class RabbitMQService:
    def __init__(self, host='rabbitmq_python', port=5672, username='guest', password='guest', queue_name='store_head'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Connect to RabbitMQ server."""
        while True:
            try:
                print("Trying to connect to RabbitMQ...")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=pika.PlainCredentials(self.username, self.password),
                        heartbeat=600,  # tambahkan heartbeat
                        blocked_connection_timeout=300,  # tambahkan timeout
                        socket_timeout=10
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
            self.channel.basic_publish(
                exchange='', 
                routing_key=queue_name, 
                body=message, 
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            print(f" [x] Sent '{message}' to queue '{queue_name}'")
        except Exception as e:
            print(f"Failed to send message to queue '{queue_name}': {e}")

    def declare_queue(self):
        """Declare the queue to consume messages from."""
        if not self.channel:
            raise ValueError("Channel is not initialized. Connect to RabbitMQ first.")
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def start_consuming(self, callback):
        """Start consuming messages from the queue."""
        if not self.channel:
            raise ValueError("Channel is not initialized. Connect to RabbitMQ first.")
        
        print(' [*] Start consume for messages. To exit press CTRL+C')

        def default_callback(ch, method, properties, body):
             message = body.decode()
             print(f" [x] Received {message}")
             ch.basic_ack(delivery_tag=method.delivery_tag)

        # Use provided callback or default
        process_callback = callback or default_callback

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=process_callback, auto_ack=False
        )
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n [x] Stopping consumer...")
            self.close_connection()

    def close_connection(self):
        """Menutup koneksi ke RabbitMQ"""
        if self.connection:
            self.connection.close()
            print("Connection closed.")
        else:
            print("No active connection to close.")