import mysql.connector
import json
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to get the resource path for PyInstaller compatibility
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load configuration from config.json
try:
    with open(resource_path("assets/config.json")) as f:
        config = json.load(f)
except Exception as e:
    logging.error(f"Failed to load config.json: {e}")
    raise

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=config["mysql"]["host"],
                user=config["mysql"]["user"],
                password=config["mysql"]["password"],
                database=config["mysql"]["database"],
                port=config["mysql"]["port"]
            )
            logging.debug("Database connection established")
        except mysql.connector.Error as err:
            logging.error(f"Error connecting to database: {err}")
            raise

    def get_connection(self):
        """Return the current connection or create a new one if closed."""
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.debug("Database connection closed")

    def __enter__(self):
        """Support for context manager."""
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection when exiting context."""
        self.close()