
import os
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker")
    )


def test_connection():
    try:
        connection = get_db_connection()
        if connection.is_connected():
            print("Successfully connected to MySQL!")
        connection.close()
    except Error as error:
        print(f"Database connection failed: {error}")


if __name__ == "__main__":
    test_connection()
