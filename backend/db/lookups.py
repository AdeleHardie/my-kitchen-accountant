from psycopg2.extensions import connection as Connection
from fastapi import HTTPException
from api.models.recipes import RecipeResponse


class BrandLookup:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection
        self.brand_map = self._load_brands()

    def _add_brand(self, brand_name: str):
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO brands (name) VALUES ($${brand_name}$$) RETURNING brand_id"
            )
            return cursor.fetchone()[0]

    def _load_brands(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, brand_id FROM brands")
            return {name: brand_id for name, brand_id in cursor.fetchall()}

    def get_id(self, brand_name: str):
        if brand_name not in self.brand_map:
            # brands are added dynamically, so update here to add new brands as needed
            brand_id = self._add_brand(brand_name)
            self.brand_map[brand_name] = brand_id
        return self.brand_map[brand_name]
    

class RecipeLookup:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection

    def get_recipe(self, id: int):
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM recipes WHERE recipe_id = {id}")
            result = cursor.fetchone()
            if not result:
                raise HTTPException(404, f"Recipe with ID {id} not found.")
            return RecipeResponse.from_query(result)
    

class ShopLookup:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection
        self.shop_map = self._load_shops()

    def _load_shops(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, shop_id FROM shops")
            return {name: shop_id for name, shop_id in cursor.fetchall()}

    def get_id(self, shop_name: str):
        if shop_name not in self.shop_map:
            raise ValueError(f"Shop '{shop_name}' not found in database.")
        return self.shop_map[shop_name]


class UnitLookup:
    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection
        self.unit_map = self._load_units()

    def _load_units(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT name, unit_id FROM units")
            return {name: unit_id for name, unit_id in cursor.fetchall()}

    def get_id(self, unit_name: str):
        if unit_name not in self.unit_map:
            raise ValueError(f"Unit '{unit_name}' not found in database.")
        return self.unit_map[unit_name]