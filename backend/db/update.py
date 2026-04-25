# --- Standard libraries ---
from datetime import datetime
from typing import List

# --- DB imports ---
from psycopg2.errors import ForeignKeyViolation
from psycopg2.extensions import connection as Connection

# --- Models ---
from scraping.models import ScrapedIngredient

# --- API ---
from api.models.recipes import CreateRecipeRequest, RecipeResponse
from fastapi import HTTPException


class BaseUpdater:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection


class IngredientUpdater(BaseUpdater):
    def update_ingredients(self, ingredients: List[ScrapedIngredient]):
        with self.db_connection.cursor() as cursor:
            for ingredient in ingredients:
                cursor.execute(f"""
                    INSERT INTO ingredients (name, brand_id, price, quantity, unit_id, normalized_quantity, normalized_unit_id, product_url, shop_id, last_updated)
                    VALUES {ingredient.to_sql()}
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


class RecipeUpdater(BaseUpdater):
    def create_recipe(self, recipe: CreateRecipeRequest):
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute(f"""
                    INSERT INTO recipes (user_id, name, number_of_portions)
                    VALUES {recipe.to_sql()}
                    RETURNING recipe_id
                """)
                new_recipe_id = cursor.fetchone()[0]
                return int(new_recipe_id)
            except ForeignKeyViolation:
                raise HTTPException(400, f"No user with ID {recipe.user_id} found.")
            except Exception as e:
                raise HTTPException(400, f"Recipe creation failed. Exception raised: {e}")