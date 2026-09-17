# crawler

A simple website crawler that summarizes each page it visits using a local LLM served by [Ollama](https://ollama.com).

## How it works

- Starts at a URL and does a breadth-first crawl, following same-domain links up to a configurable depth/page limit.
- Respects `robots.txt` by default.
- Extracts each page's title and visible text with BeautifulSoup.
- Sends the text to a local Ollama model for a short summary.

## Setup

### 1. Ollama

Install [Ollama](https://ollama.com), make sure it's running, and pull a model:

```bash
ollama pull llama3.2
```

### 2. Python environment

Requires Python 3.10+. Create a virtual environment and install the dependencies.

**Linux / macOS / WSL**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell / cmd)**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**PyCharm**

Settings → Project → Python Interpreter → Add Interpreter → Virtualenv, location `.venv` in the project folder, then install `requirements.txt` when prompted.

## Usage

With the virtual environment activated:

### Web UI

```bash
python app.py
```

Open http://localhost:5000, enter a start page and watch pages arrive with their summaries as the crawl runs.

### CLI

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

## Troubleshooting

- `ModuleNotFoundError: No module named 'bs4'` – the virtual environment isn't activated or the dependencies aren't installed. Re-run the setup steps above.
- `warning: local model unavailable` – Ollama isn't running on `http://localhost:11434` or the model hasn't been pulled.
