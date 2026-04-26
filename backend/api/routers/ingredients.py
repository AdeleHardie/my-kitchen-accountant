from fastapi import APIRouter, Depends, Query
from psycopg2.extensions import connection as Connection
from typing import Annotated

from db.connection import get_db_connection
from schemas.ingredients import IngredientResponse
from services.ingredients import IngredientManager


router = APIRouter(
    prefix="/ingredients"
)


@router.get("/search/", response_model=list[IngredientResponse])
def search_for_ingredient(
    name: Annotated[list[str] | None, Query()],
    db_connection: Connection = Depends(get_db_connection),
):
    return IngredientManager(db_connection).search(name)