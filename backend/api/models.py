from datetime import datetime
from pydantic import BaseModel
from typing import Self, Tuple


class CreateRecipeRequest(BaseModel):
    name: str
    number_of_portions: float
    user_id: int

    def to_sql(self) -> str:
        return f"({self.user_id}, $${self.name}$$, {self.number_of_portions})"
    

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

