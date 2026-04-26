from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as Connection

from db.connection import get_db_connection
from schemas.recipes import CreateRecipeRequest, RecipeResponse
from services.recipes import RecipeManager


router = APIRouter(
    prefix="/recipes"
)


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db_connection: Connection = Depends(get_db_connection),
):
    return RecipeManager(db_connection).get_recipe(recipe_id)


@router.post("/create", response_model=RecipeResponse)
def create_recipe(
    request: CreateRecipeRequest,
    db_connection: Connection = Depends(get_db_connection)
):
    new_recipe_id = RecipeManager(db_connection).create_recipe(request)

    return RecipeManager(db_connection).get_recipe(new_recipe_id)