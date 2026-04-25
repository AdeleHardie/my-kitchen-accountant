from psycopg2.extensions import connection as Connection
from typing import List
from fastapi import HTTPException
from api.models.ingredients import IngredientResponse
from api.models.recipes import RecipeResponse


class BaseLookup:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection
        self._load_map()

    def _load_map(self):
        pass


class BrandLookup(BaseLookup):
    def _add_brand(self, brand_name: str):
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO brands (name) VALUES ($${brand_name}$$) RETURNING brand_id"
            )
            return cursor.fetchone()[0]

    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, brand_id FROM brands")
            self.brand_map = {name: brand_id for name, brand_id in cursor.fetchall()}

    def get_id(self, brand_name: str):
        if brand_name not in self.brand_map:
            # brands are added dynamically, so update here to add new brands as needed
            brand_id = self._add_brand(brand_name)
            self.brand_map[brand_name] = brand_id
        return self.brand_map[brand_name]
    

class IngredientLookup(BaseLookup):
    def search(self, names: List[str]) -> List[IngredientResponse]:
        with self.db_connection.cursor() as cursor:
            filters = [f"LOWER(name) LIKE '%{name}%'" for name in names]
            filter_string = "AND ".join(filters)
            cursor.execute(f"SELECT * FROM ingredients WHERE {filter_string}")
            return [IngredientResponse.from_query(result) for result in cursor.fetchall()]
    

class RecipeLookup(BaseLookup):
    def get_recipe(self, id: int) -> RecipeResponse:
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM recipes WHERE recipe_id = {id}")
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, f"Recipe with ID {id} not found.")
            return RecipeResponse.from_query(result)
    

class ShopLookup(BaseLookup):
    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, shop_id FROM shops")
            self.shop_map = {name: shop_id for name, shop_id in cursor.fetchall()}

    def get_id(self, shop_name: str):
        if shop_name not in self.shop_map:
            raise ValueError(f"Shop '{shop_name}' not found in database.")
        return self.shop_map[shop_name]


class UnitLookup(BaseLookup):
    def _load_map(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, unit_id FROM units")
            self.unit_map = {name: unit_id for name, unit_id in cursor.fetchall()}

    def get_id(self, unit_name: str):
        if unit_name not in self.unit_map:
            raise ValueError(f"Unit '{unit_name}' not found in database.")
        return self.unit_map[unit_name]