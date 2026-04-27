"""Interactions with the `recipes` and `recipe_ingredients` tables in the database."""

from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation
from typing import Optional

# --- Internal imports ---
from schemas.recipes import CreateRecipeRequest, RecipeResponse
from services.base import BaseManager


class RecipeManager(BaseManager):
    def create_recipe(self, recipe: CreateRecipeRequest):
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO recipes (user_id, name, number_of_portions)
                    VALUES (%(user_id)s, %(name)s, %(number_of_portions)s)
                    RETURNING recipe_id
                    """,
                    recipe.__dict__,
                )
                new_recipe_id = cursor.fetchone()[0]
                return int(new_recipe_id)
            except ForeignKeyViolation:
                raise HTTPException(400, f"No user with ID {recipe.user_id} found.")
            except Exception as e:
                raise HTTPException(400, f"Recipe creation failed. Exception raised: {e}")
            
    def get_recipe(self, id: int) -> RecipeResponse:
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE recipe_id = %s", (id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, f"Recipe with ID {id} not found.")
            return RecipeResponse.from_query(result)
        

def RecipeIngredientManager(BaseManager):
    def update_ingredient(
        recipe_id: int,
        ingredient_id: int,
        quantity: Optional[float] = None,
        unit_id: Optional[float] = None,
    ):
        pass