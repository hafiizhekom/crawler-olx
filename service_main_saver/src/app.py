from rabbitmq_service import RabbitMQConsumer
from sqlite_service import SQLiteService

if __name__ == "__main__":
    
    sqlite_service = SQLiteService()
    consumer = RabbitMQConsumer()
    consumer.connect()
    consumer.declare_queue()
    consumer.start_consuming(sqlite_service)
