from fastapi import APIRouter, Depends, Query
from psycopg2.extensions import connection as Connection
from typing import Annotated

from api.models.ingredients import IngredientResponse
from db.connection import get_db_connection
from db.lookups import IngredientLookup


router = APIRouter(
    prefix="/ingredients"
)


@router.get("/search/", response_model=list[IngredientResponse])
def search_for_ingredient(
    name: Annotated[list[str] | None, Query()],
    db_connection: Connection = Depends(get_db_connection),
):
    return IngredientLookup(db_connection).search(name)