"""Interactions with the `recipes` and `recipe_ingredients` tables in the database."""

from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation

# --- Internal imports ---
from schemas.recipes import CreateRecipeRequest, RecipeResponse
from services.base import BaseManager


class RecipeManager(BaseManager):
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
            
    def get_recipe(self, id: int) -> RecipeResponse:
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM recipes WHERE recipe_id = {id}")
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, f"Recipe with ID {id} not found.")
            return RecipeResponse.from_query(result)