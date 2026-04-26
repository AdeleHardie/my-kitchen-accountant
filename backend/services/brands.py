"""Interactions with the `brands` table in the database."""

# --- Internal imports ---
from services.base import BaseManager

class BrandManager(BaseManager):
    def _add_brand(self, brand_name: str):
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO brands (name) VALUES ($${brand_name}$$) RETURNING brand_id"
            )
            return cursor.fetchone()[0]

    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, brand_id FROM brands")
            self.brand_map = {name: brand_id for name, brand_id in cursor.fetchall()}

    def get_id(self, brand_name: str):
        if brand_name not in self.brand_map:
            # brands are added dynamically, so update here to add new brands as needed
            brand_id = self._add_brand(brand_name)
            self.brand_map[brand_name] = brand_id
        return self.brand_map[brand_name]