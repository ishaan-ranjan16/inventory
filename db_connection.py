
import psycopg2


# PostgreSQL connection function
def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="inventory_db",
        user="postgres",
        password="1234",
        port=5432
    )
    return conn