from web_scraper import WebScraper

if __name__ == "__main__":
    # Initialize WebScraper with JavaScript rendering enabled
    scraper = WebScraper(enable_js=True)

    # Example URLs, including JavaScript-heavy sites
    urls = [
        "https://en.wikipedia.org/wiki/Web_scraping",  # Non-JavaScript page
        "https://www.python.org/",  # Another simple page
        "https://www.nytimes.com/",  # JavaScript-heavy page
    ]

    results = scraper.scrape_multiple_pages(urls)

    for url, data in results.items():
        print(f"\nURL: {url}")
        print(f"Title: {data['title']}")
        print(f"Description: {data['description']}")
        print(f"Keywords: {data['keywords']}")
        print(f"Content (first 500 chars): {data['content'][:500]}...")
        print(f"Links: {data['links']}")
