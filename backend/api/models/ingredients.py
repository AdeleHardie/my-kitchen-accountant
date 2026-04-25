from pydantic import BaseModel
from typing import Tuple, Self


class IngredientResponse(BaseModel):
    ingredient_id: int
    name: str
    brand_id: int
    price: float
    quantity: float
    unit_id: int
    normalized_quantity: float
    normalized_unit_id: int
    shop_id: int
    not_found: bool

    @classmethod
    def from_query(cls, query_result: Tuple) -> Self:
        return cls(
            ingredient_id=query_result[0],
            name=query_result[1],
            brand_id=query_result[2],
            price=query_result[3],
            quantity=query_result[4],
            unit_id=query_result[5],
            normalized_quantity=query_result[6],
            normalized_unit_id=query_result[7],
            shop_id=query_result[9],
            not_found=query_result[11],
        )
