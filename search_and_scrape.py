import argparse
import json
import csv
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from diskcache import Cache
from search import SearchModule
from web_scraper import WebScraper
from ollama import LLMIntegration


class SearchAndScrape:
    def __init__(self, max_results=5, cache_dir="cache", llm_model="llama3.1:latest"):
        """
        Initialize the SearchAndScrape tool.

        Args:
            max_results (int): Maximum number of search results to fetch.
            cache_dir (str): Directory to store cached results.
            llm_model (str): Model to use with the LLM integration.
        """
        self.search_module = SearchModule(max_results=max_results)
        self.web_scraper = WebScraper()
        self.llm = LLMIntegration(model=llm_model)
        self.console = Console()
        self.cache = Cache(cache_dir)

    def search_and_scrape(self, query, skip_restricted=True, time_range=None, include_keywords=None, exclude_keywords=None):
        """
        Perform a search and scrape operation.

        Args:
            query (str): User's search query.
            skip_restricted (bool): Skip pages restricted by robots.txt.
            time_range (str): Time range for search ('d', 'w', 'm', 'y', 'none').
            include_keywords (list): Keywords to include in search results.
            exclude_keywords (list): Keywords to exclude from search results.

        Returns:
            dict: Results and final answer.
        """
        self.console.print(f"[cyan]Original Query: {query}[/cyan]")

        # Reformulate query using LLM
        reformulated_query = self.llm.reformulate_query(query)
        self.console.print(f"[cyan]Reformulated Query: {
                           reformulated_query}[/cyan]")

        # Check cache
        if reformulated_query in self.cache:
            self.console.print(
                "[green]Loaded cached results for query.[/green]")
            return self.cache[reformulated_query]

        # Perform search
        search_results = self.search_module.search(
            reformulated_query,
            time_range=time_range,
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
        )

        # Handle no search results
        if not search_results:
            self.console.print("[red]No search results found.[/red]")
            return {"results": [], "final_answer": None}

        # Scrape URLs
        urls = [result["link"] for result in search_results]
        combined_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console,
        ) as progress:
            scrape_task = progress.add_task(
                "Scraping URLs...", total=len(urls))
            scraped_data = {}

            for url in urls:
                try:
                    scraped_data[url] = self.web_scraper.scrape_page(url)
                except Exception as e:
                    self.console.print(f"[red]Error scraping {url}: {e}[/red]")
                progress.advance(scrape_task)

        # Compile results
        for result in search_results:
            url = result["link"]
            scraped_content = scraped_data.get(url, {})
            if skip_restricted and "Access denied by robots.txt" in scraped_content.get("content", ""):
                self.console.print(
                    f"[yellow]Skipped restricted page: {url}[/yellow]")
                continue

            combined_results.append({
                "title": result["title"],
                "snippet": result["snippet"],
                "link": url,
                "scraped_content": scraped_content.get("content", "No content scraped."),
                "source": urlparse(url).netloc,
            })

        # Generate final answer
        scraped_text = " ".join([res["scraped_content"]
                                for res in combined_results])
        self.console.print("[cyan]Generating final answer using LLM...[/cyan]")
        final_answer = self.llm.generate_final_answer(query, scraped_text)

        # Cache results
        data = {"results": combined_results, "final_answer": final_answer}
        self.cache[reformulated_query] = data
        return data

    def display_results(self, data):
        """
        Display search results and the final answer.

        Args:
            data (dict): Search results and final answer.
        """
        results = data.get("results", [])
        final_answer = data.get("final_answer", "No final answer generated.")

        # Display search results
        table = Table(title="Search and Scrape Results")
        table.add_column("Title", style="cyan", no_wrap=True)
        table.add_column("Snippet", justify="left")
        table.add_column("Source", style="magenta")

        for result in results:
            table.add_row(result["title"], result["snippet"], result["source"])

        self.console.print(table)
        self.console.print(
            f"[bold green]Final Answer:[/bold green] {final_answer}")

    def export_results(self, data, output_format="json"):
        """
        Export results to a file.

        Args:
            data (dict): Results to export.
            output_format (str): Format for export ('json' or 'csv').
        """
        if output_format == "json":
            with open("search_and_scrape_results.json", "w") as f:
                json.dump(data, f, indent=4)
            self.console.print(
                "[green]Results exported to search_and_scrape_results.json[/green]")
        elif output_format == "csv":
            with open("search_and_scrape_results.csv", "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["title", "snippet", "link", "source"])
                writer.writeheader()
                writer.writerows(data.get("results", []))
            self.console.print(
                "[green]Results exported to search_and_scrape_results.csv[/green]")
        else:
            self.console.print(
                "[red]Unsupported format. Use 'json' or 'csv'.[/red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search and scrape web content.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--re", type=int, default=5,
                        help="Number of results to fetch")
    parser.add_argument("--time_range", type=str, default="none",
                        choices=["d", "w", "m", "y", "none"], help="Time range for search")
    parser.add_argument("--include", type=str,
                        help="Comma-separated keywords to include in results")
    parser.add_argument("--exclude", type=str,
                        help="Comma-separated keywords to exclude from results")
    parser.add_argument("--export", type=str, default="json",
                        choices=["json", "csv"], help="Export format for results")

    args = parser.parse_args()

    include_keywords = [kw.strip() for kw in args.include.split(
        ",")] if args.include else None
    exclude_keywords = [kw.strip() for kw in args.exclude.split(
        ",")] if args.exclude else None

    search_and_scrape = SearchAndScrape(max_results=args.re)
    data = search_and_scrape.search_and_scrape(
        query=args.query,
        time_range=args.time_range,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
    )

    if data.get("results"):
        search_and_scrape.display_results(data)
        search_and_scrape.export_results(data, output_format=args.export)
