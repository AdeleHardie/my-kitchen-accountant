"""Lightweight ingredient class for representing scraped food items."""

from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# -- Database lookups
from services.brands import BrandManager
from services.units import UnitManager


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
        brand_lookup: BrandManager,
        unit_lookup: UnitManager,
        timestamp: str,
    ):
        # hoping it will always at least have a name
        name = web_element.find_element(By.CLASS_NAME, "product-tile__name").text
        try:
            quantity_unit_str = web_element.find_element(By.CLASS_NAME, "product-tile__selling-size-and-comparison").text
            if quantity_unit_str == "":
                quantity = 1.0
                unit = "EACH"
            else:
                quantity, unit = quantity_unit_str.splitlines()[0].split()
                if "£" in quantity:
                    quantity = quantity.split("/")[1]
                quantity = float(quantity.replace(",", ""))
                unit = unit.upper()

            price_str = web_element.find_element(By.CLASS_NAME, "base-price").text
            last_price_in_str = price_str.split("£")[-1].strip()
            if "/" in last_price_in_str:
                price_parts = last_price_in_str.split("/")
                price = float(price_parts[0])
                quantity, unit = price_parts[1].split()
                quantity = float(quantity)
                unit = unit.upper()
            else:
                price = float(last_price_in_str)

            if unit in ["PACK"]:
                unit = "EACH"
            normalized_quantity, normalized_unit = normalize_unit(quantity, unit)

            base_link = web_element.find_element(By.CLASS_NAME, "base-link").get_attribute("href")

            return cls(
                name=name,
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
        except Exception as e:
            print(f"Could not parse ingredient with name {name}:\n{e}")
            print(f"Ingredient web element text: {web_element.text}")
            return None
    
    def to_sql(self):
        return f"($${self.name}$$, {self.brand_id}, {self.price}, {self.quantity}, {self.unit_id}, {self.normalized_quantity}, {self.normalized_unit_id}, '{self.product_url}', {self.shop_id}, '{self.last_updated}')"


def normalize_unit(quantity: float, unit: str): 
    if unit in ["KG", "G"]:
        normalized_quantity = quantity * 1000 if unit == "KG" else quantity
        normalized_unit = "G"
    elif unit in ["L", "CL", "ML"]:
        volume_map = {"L": 1000, "CL": 10, "ML": 1}
        normalized_quantity = quantity * volume_map[unit]
        normalized_unit = "ML"
    else:
        normalized_quantity = quantity
        normalized_unit = unit

    return normalized_quantity, normalized_unit