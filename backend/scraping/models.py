"""Lightweight ingredient class for representing scraped food items."""

from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# -- Database lookups
from db.lookups import BrandLookup, ShopLookup, UnitLookup


@dataclass
class ScrapedIngredient:
    name: str
    brand_id: int
    price: float
    quantity: float
    unit_id: int
    normalized_quantity: float
    normalized_unit_id: int
    product_url: str
    shop_id: int
    last_updated: str
    not_found: bool = False

    @classmethod
    def from_aldi_web_element(
        cls,
        web_element: WebElement,
        shop_id: int,
        brand_lookup: BrandLookup,
        unit_lookup: UnitLookup,
        timestamp: str,
    ):
        price_str = web_element.find_element(By.CLASS_NAME, "base-price").text
        price = float(price_str.split("£")[-1].strip())

        quantity_unit_str = web_element.find_element(By.CLASS_NAME, "product-tile__selling-size-and-comparison").text
        if quantity_unit_str == "":
            quantity = 1.0
            unit = "EACH"
        else:
            quantity, unit = quantity_unit_str.splitlines()[0].split()
            quantity = float(quantity.replace(",", ""))
            unit = unit.upper()

        normalized_quantity, normalized_unit = normalize_unit(quantity, unit)

        base_link = web_element.find_element(By.CLASS_NAME, "base-link").get_attribute("href")

        return cls(
            name=web_element.find_element(By.CLASS_NAME, "product-tile__name").text,
            brand_id=brand_lookup.get_id(web_element.find_element(By.CLASS_NAME, "product-tile__brandname").text),
            price=price,
            quantity=quantity,
            unit_id=unit_lookup.get_id(unit),
            normalized_quantity=normalized_quantity,
            normalized_unit_id=unit_lookup.get_id(normalized_unit),
            product_url=base_link,
            shop_id=shop_id,
            last_updated=timestamp,
        )
    
    def to_sql(self):
        return f"($${self.name}$$, {self.brand_id}, {self.price}, {self.quantity}, {self.unit_id}, {self.normalized_quantity}, {self.normalized_unit_id}, '{self.product_url}', {self.shop_id}, '{self.last_updated}')"


def normalize_unit(quantity: float, unit: str):
    if unit in ["KG", "G"]:
        normalized_quantity = quantity * 1000 if unit == "KG" else quantity
        normalized_unit = "G"
    elif unit in ["L", "ML"]:
        normalized_quantity = quantity * 1000 if unit == "L" else quantity
        normalized_unit = "ML"
    else:
        normalized_quantity = quantity
        normalized_unit = unit

    return normalized_quantity, normalized_unit