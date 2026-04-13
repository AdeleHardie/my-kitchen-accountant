# --- Standard libraries
from datetime import datetime

# --- Web scraping ---
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# --- Models ---
from scraping.models import ScrapedIngredient
# --- Database ---
from db.connection import get_db_connection
from db.lookups import BrandLookup, ShopLookup, UnitLookup
from db.update import IngredientUpdater


class AldiScraper:
    URL = "https://www.aldi.co.uk"
    SECTIONS = ["fresh-food", "chilled-food", "food-cupboard", "frozen-food", "alcohol", "drinks", "bakery"]

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.db_connection = get_db_connection()
        self.shop_id = ShopLookup(self.db_connection).get_id("Aldi")
        self.brand_lookup = BrandLookup(self.db_connection)
        self.unit_lookup = UnitLookup(self.db_connection)
        self.updater = IngredientUpdater(self.db_connection)

    def scrape(self):
        """For now only scrape the first 2 pages of the fresh food section."""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Starting scrape for Aldi at {self.timestamp}")
        try:
            page = 1
            while True:
                driver = webdriver.Firefox(options=self.options)
                driver.implicitly_wait(5)
                page_url = f"{self.URL}/products/frozen-food?page={page}"
                driver.get(page_url)
                page_items = driver.find_elements(By.CLASS_NAME, "product-tile")
                if len(page_items) == 0:
                    break
                parsed_ingredients = []
                for item in page_items:
                    scraped_ingredient = ScrapedIngredient.from_aldi_web_element(
                        item,
                        self.shop_id,
                        self.brand_lookup,
                        self.unit_lookup,
                        self.timestamp,
                    )
                    parsed_ingredients.append(scraped_ingredient)
                self.updater.update_ingredients(parsed_ingredients)
                driver.quit()
                page += 1
                if page > 1:  # Limit to first 2 pages for now
                    break
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            driver.quit()

        # Mark products as not found if they were not updated during this scrape
        self.updater.update_not_found(self.shop_id, self.timestamp)

        print(f"Finished scrape for Aldi at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")