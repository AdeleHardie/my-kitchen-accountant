# --- Standard libraries
from datetime import datetime
from time import sleep

# --- Web scraping ---
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# --- Models ---
from scraping.models import ScrapedIngredient
# --- Database ---
from db.connection import get_db_connection
from services.brands import BrandManager
from services.ingredients import IngredientManager
from services.shops import ShopManager
from services.units import UnitManager


class AldiScraper:
    URL = "https://www.aldi.co.uk"
    SECTIONS = ["fresh-food", "chilled-food", "food-cupboard", "frozen-food", "alcohol", "drinks", "bakery"]

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.db_connection = get_db_connection()
        self.shop_id = ShopManager(self.db_connection).get_id("Aldi")
        self.brand_lookup = BrandManager(self.db_connection)
        self.unit_lookup = UnitManager(self.db_connection)
        self.updater = IngredientManager(self.db_connection)
        self.num_failed_ingredients = 0

    def _scrape_page(self, page: int, section: str) -> bool:
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.implicitly_wait(5)
        page_url = f"{self.URL}/products/{section}?page={page}"
        self.driver.get(page_url)
        page_items = self.driver.find_elements(By.CLASS_NAME, "product-tile")
        if len(page_items) == 0:
            print(f"Finished scraping section: {section}, after {page-1} pages.")
            return False
        parsed_ingredients = []
        for item in page_items:
            scraped_ingredient = ScrapedIngredient.from_aldi_web_element(
                item,
                self.shop_id,
                self.brand_lookup,
                self.unit_lookup,
                self.timestamp,
            )
            if scraped_ingredient:
                parsed_ingredients.append(scraped_ingredient.to_sql())
            else:
                self.num_failed_ingredients += 1
        self.updater.update_ingredients(parsed_ingredients)
        self.driver.quit()
        return True

    def scrape(self):
        """Scrape all of Aldi food products."""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Starting scrape for Aldi at {self.timestamp}")
        for section in self.SECTIONS:
            print(f"Scraping section: {section}.")
            page = 1
            section_continuing = True
            while section_continuing:
                try:
                    section_continuing = self._scrape_page(page, section)
                except Exception as e:
                    print(f"Error while scraping Aldi section {section}, page {page}.")
                    print(e)
                finally:
                    self.driver.quit()
                page += 1
                sleep(5) # wait between scrape requests

        # Mark products as not found if they were not updated during this scrape
        self.updater.update_not_found(self.shop_id, self.timestamp)

        print(f"Finished scrape for Aldi at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.num_failed_ingredients == 0:
            print("All ingredients parsed successfully.")
        else:
            print(f"Parsing failed for {self.num_failed_ingredients} ingredients.")