"""Base for all interaction with database services."""

from psycopg2.extensions import connection as Connection

class BaseManager:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection
        self._load_map()

    def _load_map(self):
        pass