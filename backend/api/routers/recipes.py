from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extensions import connection as Connection

from api.models.recipes import CreateRecipeRequest, RecipeResponse
from db.connection import get_db_connection
from db.lookups import RecipeLookup
from db.update import RecipeUpdater


router = APIRouter(
    prefix="/recipes"
)


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db_connection: Connection = Depends(get_db_connection),
):
    return RecipeLookup(db_connection).get_recipe(recipe_id)


@router.post("/create", response_model=RecipeResponse)
def create_recipe(
    request: CreateRecipeRequest,
    db_connection: Connection = Depends(get_db_connection)
):
    new_recipe_id = RecipeUpdater(db_connection).create_recipe(request)

    return RecipeLookup(db_connection).get_recipe(new_recipe_id)