import argparse
from search_and_scrape import SearchAndScrape
from rich.console import Console


def main():
    """
    Main function to interact with the Search and Scrape tool.
    Provides a command-line interface for searching, scraping, and generating answers.
    """
    console = Console()

    parser = argparse.ArgumentParser(
        description="Search and Scrape Web Content Using LLM Integration")
    parser.add_argument("--query", type=str,
                        help="The search query to execute")
    parser.add_argument("--results", type=int, default=5,
                        help="Number of search results to fetch (default: 5)")
    parser.add_argument("--time_range", type=str, choices=["d", "w", "m", "y", "none"], default="none",
                        help="Time range for search ('d' for day, 'w' for week, etc., default: 'none')")
    parser.add_argument("--include", type=str,
                        help="Comma-separated keywords to include in search results")
    parser.add_argument("--exclude", type=str,
                        help="Comma-separated keywords to exclude from search results")
    parser.add_argument("--export", type=str, choices=["json", "csv"], default="json",
                        help="Export format for results (default: 'json')")

    args = parser.parse_args()

    # Ensure a query is provided
    if not args.query:
        console.print("[red]Error: A search query must be provided.[/red]")
        return

    # Parse include/exclude keywords
    include_keywords = [kw.strip() for kw in args.include.split(
        ",")] if args.include else None
    exclude_keywords = [kw.strip() for kw in args.exclude.split(
        ",")] if args.exclude else None

    # Initialize Search and Scrape
    search_and_scrape = SearchAndScrape(max_results=args.results)

    console.print("[bold cyan]Executing Search and Scrape...[/bold cyan]")

    # Perform the search and scrape operation
    try:
        data = search_and_scrape.search_and_scrape(
            query=args.query,
            time_range=args.time_range,
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
        )

        # Display results
        if data.get("results"):
            console.print(
                "[green]Search and Scrape completed successfully.[/green]")
            search_and_scrape.display_results(data)

            # Export results if required
            search_and_scrape.export_results(data, output_format=args.export)
        else:
            console.print("[yellow]No results found or processed.[/yellow]")

    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")


if __name__ == "__main__":
    main()
