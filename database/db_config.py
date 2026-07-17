import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT"))
        )

        return connection

    except mysql.connector.Error as err:
        print("Database Connection Error:", err)
        return None