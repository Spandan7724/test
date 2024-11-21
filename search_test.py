from search import SearchModule


if __name__ == "__main__":
    search_module = SearchModule(max_results=5)

    # Test query
    query = input("Enter your search query: ")
    results = search_module.search(query)

    if results:
        print("\nSearch Results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            print(f"Snippet: {result['snippet']}")
    else:
        print("No results found.")
