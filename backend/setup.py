from db.init_db import init_db
from scraping.scraper import AldiScraper


def main():
    init_db()
    AldiScraper().scrape()


if __name__ == "__main__":
    main()