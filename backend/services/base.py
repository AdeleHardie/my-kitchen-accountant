"""Base for all interaction with database services."""

from psycopg2.extensions import connection as Connection

# --- Internal imports ---
from core.auth import User

class BaseManager:
    def __init__(
        self,
        user: User,
        db_connection: Connection,
    ):
        self.user_id = user.id
        self.db_connection = db_connection
        self._load_map()

    def _load_map(self):
        pass