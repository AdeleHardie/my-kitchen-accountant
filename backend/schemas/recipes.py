from datetime import datetime
from fastapi import HTTPException
from pydantic import AfterValidator, BaseModel
from typing import Annotated, Self, Tuple


def greater_than_zero(value: float) -> float:
    if value <= 0:
        raise HTTPException(400, f"Recipe portions must be greater than zero, got: {value}")
    return value


class CreateRecipeRequest(BaseModel):
    name: str
    number_of_portions: Annotated[float, AfterValidator(greater_than_zero)]
    user_id: int
    

class RecipeResponse(BaseModel):
    recipe_id: int
    user_id: int
    name: str
    number_of_portions: float
    date_created: datetime

    @classmethod
    def from_query(cls, query_result: Tuple) -> Self:
        return cls(
            recipe_id=query_result[0],
            user_id=query_result[1],
            name=query_result[2],
            number_of_portions=query_result[3],
            date_created=query_result[4],
        )


class RecipeIngredientResponse(BaseModel):
    recipe_ingredient_id: int
    recipe_id: int
    ingredient_id: int
    quantity: float
    unit_id: int
    normalized_quantity: float
    normalized_unit_id: int

    @classmethod
    def from_query(cls, query_result: Tuple) -> Self:
        return cls(
            recipe_ingredient_id=query_result[0],
            recipe_id=query_result[1],
            ingredient_id=query_result[2],
            quantity=query_result[3],
            unit_id=query_result[4],
            normalized_quantity=query_result[5],
            normalized_unit_id=query_result[6],
        )