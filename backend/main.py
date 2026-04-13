from scraping.scraper import AldiScraper


def main():
    aldi_items = AldiScraper().scrape()
    print(f"Scraped {len(aldi_items)} items from Aldi.")
    for item in aldi_items:
        print(item.to_csv())


if __name__ == "__main__":
    main()
