import pika
import time

def connect_to_rabbitmq():
    while True:
        try:
            print("Trying to connect to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq_python',  # Hostname sesuai dengan Docker Compose
                    port=5672,
                    credentials=pika.PlainCredentials('guest', 'guest')
                )
            )
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}")
            time.sleep(5)

# Establish connection
connection = connect_to_rabbitmq()
channel = connection.channel()

# Proceed with RabbitMQ operations
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
