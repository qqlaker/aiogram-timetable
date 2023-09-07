import sqlite3
import os

from dotenv.main import load_dotenv

load_dotenv("config/.env")


class DatabaseConnection(object):
    def __init__(
            self,
            database=os.getenv("DATABASE_FILE")
    ):
        self.connection = None
        self.database = database

    def __enter__(self):
        self.connection = sqlite3.connect(self.database)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
