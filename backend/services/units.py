"""Interactions with the `units` table in the database."""

# --- Internal imports ---
from services.base import BaseManager


class UnitManager(BaseManager):
    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, unit_id FROM units")
            self.unit_map = {name: unit_id for name, unit_id in cursor.fetchall()}

    def get_id(self, unit_name: str):
        if unit_name not in self.unit_map:
            raise ValueError(f"Unit '{unit_name}' not found in database.")
        return self.unit_map[unit_name]