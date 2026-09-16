# crawler

A simple website crawler that summarizes each page it visits using a local LLM served by [Ollama](https://ollama.com).

## How it works

- Starts at a URL and does a breadth-first crawl, following same-domain links up to a configurable depth/page limit.
- Respects `robots.txt` by default.
- Extracts each page's title and visible text with BeautifulSoup.
- Sends the text to a local Ollama model for a short summary.

## Setup

Requires [Ollama](https://ollama.com) running locally with a model pulled, e.g.:

```bash
ollama pull llama3.2
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py https://example.com --max-pages 10 --max-depth 2
```

Options:

- `--max-pages` – maximum number of pages to visit (default 20)
- `--max-depth` – maximum link depth from the start URL (default 2)
- `--delay` – seconds to wait between requests (default 0.5)
- `--model` – Ollama model name to use for summaries (default `llama3.2`)
- `--no-robots` – ignore `robots.txt`
- `--output` / `-o` – write results as JSON to a file

If the Ollama server isn't reachable, the crawler still runs and simply skips summaries.
