"""Interactions with the `recipes` and `recipe_ingredients` tables in the database."""

from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation
from typing import Optional

# --- Internal imports ---
from schemas.recipes import (
    CreateRecipeRequest,
    RecipeResponse,
    RecipeIngredientResponse,
)
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
            
    def delete_recipe(self, id: int) -> str:
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM recipes WHERE recipe_id = %s RETURNING recipe_id", (id,))
                result = cursor.fetchall()
                if len(result) == 0:
                    raise HTTPException(404, f"Recipe with ID {id} not found.")
                return f"Recipe with ID {id} deleted successfully."
            except Exception as e:
                raise HTTPException(400, f"Could not delete recipe with ID {id}: {e}")
            
    def get_recipe(self, id: int) -> RecipeResponse:
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE recipe_id = %s", (id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, f"Recipe with ID {id} not found.")
            return RecipeResponse.from_query(result)
        

class RecipeIngredientManager(BaseManager):
    def update_ingredient(
        self,
        recipe_id: int,
        ingredient_id: int,
        quantity: Optional[float] = None,
        unit_id: Optional[float] = None,
    ) -> RecipeIngredientResponse:
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (recipe_id, ingredient_id) DO UPDATE SET
                        quantity = EXCLUDED.quantity,
                        unit_id = EXCLUDED.unit_id
                    RETURNING recipe_ingredient_id, recipe_id, ingredient_id, quantity, unit_id, normalized_quantity, normalized_unit_id
                    """,
                    (recipe_id, ingredient_id, quantity, unit_id),
                )
                result = cursor.fetchone()
                return RecipeIngredientResponse.from_query(result)
            except Exception as e:
                raise HTTPException(400, f"Unable to add or update recipe ingredient: {e}")