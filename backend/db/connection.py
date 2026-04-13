from psycopg2 import connect
from psycopg2.extensions import connection as Connection

# --- Internal imports ---
from core.config import settings


def get_db_connection() -> Connection:
    connection = connect(settings.DATABASE_URL)
    connection.autocommit = True
    return connection