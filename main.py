"""CLI for the simple local-LLM website crawler."""

import argparse
import json
import sys

from crawler import Crawler
from llm import DEFAULT_MODEL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl a website and summarize pages with a local LLM.")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--max-pages", type=int, default=20, help="Maximum number of pages to visit")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum link depth from the start URL")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between requests")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name to use for summaries")
    parser.add_argument("--no-robots", action="store_true", help="Ignore robots.txt rules")
    parser.add_argument("--output", "-o", help="Write results as JSON to this file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    crawler = Crawler(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        model=args.model,
        respect_robots=not args.no_robots,
    )

    pages = crawler.crawl()

    results = [
        {
            "url": page.url,
            "title": page.title,
            "summary": page.summary,
            "num_links": len(page.links),
        }
        for page in pages
    ]

    print(f"\nCrawled {len(pages)} page(s):\n")
    for page in results:
        print(f"- {page['title']} ({page['url']})")
        if page["summary"]:
            print(f"  {page['summary']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved results to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
