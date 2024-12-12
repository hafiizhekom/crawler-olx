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
                CREATE TABLE IF NOT EXISTS cars_head (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand TEXT,
                    model TEXT,
                    price INTEGER,
                    location TEXT,
                    url TEXT UNIQUE
                )
                """
            )

    def save_message(self, car):
        """Save a message to the database."""
        print("KOCAK")
        print(type(car))
        with self.connection:
            self.connection.execute(
                "INSERT OR IGNORE INTO cars_head (brand, model, price, location, url) VALUES (?, ?, ?, ?, ?)", 
                (
                    car['brand'],
                    car['model'],
                    car['price'],
                    car['location'],
                    car['url']
                )
            )

    def close_connection(self):
        """Close the connection to the database."""
        if self.connection:
            self.connection.close()