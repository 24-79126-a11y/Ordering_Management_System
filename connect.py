import os

import mysql.connector

def connect_database():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "ordering_management_system"),
            connection_timeout=5,
        )

    except (mysql.connector.Error, ValueError):
        return None
