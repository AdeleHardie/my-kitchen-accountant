"""Interactions with the `ingredients` table in the database."""

from typing import List

# --- Internal imports ---
from schemas.ingredients import IngredientResponse
from services.base import BaseManager


class IngredientManager(BaseManager):
    def search(self, names: List[str]) -> List[IngredientResponse]:
        with self.db_connection.cursor() as cursor:
            filters = [f"LOWER(name) LIKE '%{name}%'" for name in names]
            filter_string = "AND ".join(filters)
            cursor.execute(f"SELECT * FROM ingredients WHERE {filter_string}")
            return [IngredientResponse.from_query(result) for result in cursor.fetchall()]
        
    def update_ingredients(self, ingredients: List[str]):
        with self.db_connection.cursor() as cursor:
            for ingredient in ingredients:
                cursor.execute(f"""
                    INSERT INTO ingredients (name, brand_id, price, quantity, unit_id, normalized_quantity, normalized_unit_id, product_url, shop_id, last_updated)
                    VALUES {ingredient}
                    ON CONFLICT (product_url) DO UPDATE SET
                        price = EXCLUDED.price,
                        quantity = EXCLUDED.quantity,
                        unit_id = EXCLUDED.unit_id,
                        normalized_quantity = EXCLUDED.normalized_quantity,
                        normalized_unit_id = EXCLUDED.normalized_unit_id,
                        last_updated = EXCLUDED.last_updated,
                        not_found = FALSE
                """)

    def update_not_found(self, shop_id: int, timestamp: str):
        """Mark products as not found if they were not updated during the latest scrape."""
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ingredients
                SET not_found = TRUE
                WHERE shop_id = {shop_id} AND last_updated < '{timestamp}'
            """)
            print(f"{cursor.rowcount} ingredients previously in database not found in this scrape.")