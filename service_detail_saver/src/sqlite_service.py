import sqlite3

class SQLiteService:
    def __init__(self, db_name="messages.db"):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Connect to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        """Create a table for storing messages if it doesn't exist."""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS car_detail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    car_id INTEGER,
                    color TEXT,
                    body_type TEXT,
                    seller_type TEXT,
                    car_exchange TEXT
                )
                """
            )

    def save_message(self, car):
        try:
            """Save a message to the database."""
            with self.connection:
                cursor = self.connection.execute(
                    """INSERT OR IGNORE INTO car_detail (car_id, color, body_type, seller_type, car_exchange) VALUES (?, ?, ?, ?, ?)""", 
                    (
                        car['car_id'],
                        car['color'],
                        car['body_type'],
                        car['seller_type'],
                        car['car_exchange']
                    )
                )
                print(f"Data '{car}' saved" )
                return cursor.lastrowid
        except Exception as e:
            print(f"Error: {e}")
            return False

    def close_connection(self):
        """Close the connection to the database."""
        if self.connection:
            self.connection.close()