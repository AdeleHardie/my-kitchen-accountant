from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as Connection
from typing import List, Optional

from core.auth import get_current_user, User
from db.connection import get_db_connection
from schemas.recipes import CreateRecipeRequest, RecipeResponse
from services.recipes import RecipeManager, RecipeIngredientManager


router = APIRouter(
    prefix="/recipes"
)


@router.get("/all", response_model=List[RecipeResponse])
def get_all_recipes(
    user: User = Depends(get_current_user),
    db_connection: Connection = Depends(get_db_connection)
):
    return RecipeManager(user, db_connection).get_all_recipes()


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db_connection: Connection = Depends(get_db_connection),
):
    return RecipeManager(user, db_connection).get_recipe(recipe_id)


@router.post("/create", response_model=RecipeResponse)
def create_recipe(
    request: CreateRecipeRequest,
    user: User = Depends(get_current_user),
    db_connection: Connection = Depends(get_db_connection)
):
    request.user_id = user.id
    new_recipe_id = RecipeManager(user, db_connection).create_recipe(request)

    return RecipeManager(user, db_connection).get_recipe(new_recipe_id)


@router.delete("/{recipe_id}/delete")
def delete_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db_connection: Connection = Depends(get_db_connection)
):
    return RecipeManager(user, db_connection).delete_recipe(recipe_id)


@router.post("/{recipe_id}/add/{ingredient_id}")
def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_id: int,
    quantity: Optional[float] = None,
    unit_id: Optional[float] = None,
    user: User = Depends(get_current_user),
    db_connection: Connection = Depends(get_db_connection),
):
    return RecipeIngredientManager(user, db_connection).update_ingredient(recipe_id, ingredient_id, quantity, unit_id)