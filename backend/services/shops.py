"""Interactions with the `shops` table in the database."""

# --- Internal imports ---
from services.base import BaseManager


class ShopManager(BaseManager):
    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, shop_id FROM shops")
            self.shop_map = {name: shop_id for name, shop_id in cursor.fetchall()}

    def get_id(self, shop_name: str):
        if shop_name not in self.shop_map:
            raise ValueError(f"Shop '{shop_name}' not found in database.")
        return self.shop_map[shop_name]