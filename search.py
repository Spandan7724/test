from duckduckgo_search import DDGS
from typing import List, Dict, Optional


class SearchModule:
    def __init__(self, max_results: int = 5, default_time_range: str = "none"):
        """
        Initialize the SearchModule.

        Args:
            max_results (int): The maximum number of search results to return.
            default_time_range (str): Default time range for searches ('d', 'w', 'm', 'y', 'none').
        """
        self.max_results = max_results
        self.default_time_range = default_time_range

    def search(
        self,
        query: str,
        time_range: Optional[str] = None,
        include_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query (str): The search query.
            time_range (Optional[str]): Time range for the search ('d', 'w', 'm', 'y', 'none').
            include_keywords (Optional[List[str]]): Keywords to include in the results.
            exclude_keywords (Optional[List[str]]): Keywords to exclude from the results.

        Returns:
            list: A list of filtered search results with title, link, and snippet.
        """
        time_range = time_range or self.default_time_range

        try:
            with DDGS() as ddgs:
                results = ddgs.text(
                    query, timelimit=time_range, max_results=self.max_results
                )
                filtered_results = self._filter_results(
                    results,
                    include_keywords=include_keywords,
                    exclude_keywords=exclude_keywords,
                )
                return [
                    {
                        "title": result.get("title", "No Title"),
                        "link": result.get("href", "No Link"),
                        "snippet": result.get("body", "No Snippet"),
                    }
                    for result in filtered_results
                ]
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def _filter_results(
        self,
        results: List[Dict],
        include_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Filter search results based on include and exclude keywords.

        Args:
            results (list): The raw search results.
            include_keywords (Optional[List[str]]): Keywords to include.
            exclude_keywords (Optional[List[str]]): Keywords to exclude.

        Returns:
            list: The filtered search results.
        """
        filtered_results = []

        for result in results:
            title = result.get("title", "").lower()
            snippet = result.get("body", "").lower()

            # Include filter
            if include_keywords and not any(
                keyword.lower() in title or keyword.lower() in snippet
                for keyword in include_keywords
            ):
                continue

            # Exclude filter
            if exclude_keywords and any(
                keyword.lower() in title or keyword.lower() in snippet
                for keyword in exclude_keywords
            ):
                continue

            filtered_results.append(result)

        return filtered_results


if __name__ == "__main__":
    # Example usage
    search_module = SearchModule(max_results=5, default_time_range="w")
    query = input("Enter your search query: ")

    # Allow users to specify filters
    include = input(
        "Enter keywords to include (comma-separated, or leave blank): ")
    exclude = input(
        "Enter keywords to exclude (comma-separated, or leave blank): ")

    include_keywords = [kw.strip()
                        for kw in include.split(",")] if include else None
    exclude_keywords = [kw.strip()
                        for kw in exclude.split(",")] if exclude else None

    # Perform search
    results = search_module.search(
        query, include_keywords=include_keywords, exclude_keywords=exclude_keywords
    )

    if results:
        print("\nSearch Results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            print(f"Snippet: {result['snippet']}")
    else:
        print("No results found.")
