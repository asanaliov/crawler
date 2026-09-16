"""Simple breadth-first website crawler with local-LLM page summaries."""

from __future__ import annotations

import time
import urllib.robotparser
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from llm import summarize

USER_AGENT = "simple-crawler/1.0"


@dataclass
class Page:
    url: str
    title: str
    text: str
    summary: str
    links: list[str] = field(default_factory=list)


class Crawler:
    def __init__(
        self,
        start_url: str,
        max_pages: int = 20,
        max_depth: int = 2,
        delay: float = 0.5,
        model: str | None = None,
        respect_robots: bool = True,
        timeout: float = 10.0,
    ):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay = delay
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

        self.robots = None
        if respect_robots:
            self.robots = urllib.robotparser.RobotFileParser()
            robots_url = urljoin(start_url, "/robots.txt")
            try:
                self.robots.set_url(robots_url)
                self.robots.read()
            except Exception:
                self.robots = None

    def _allowed(self, url: str) -> bool:
        if self.robots is None:
            return True
        try:
            return self.robots.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    def _same_domain(self, url: str) -> bool:
        return urlparse(url).netloc == self.domain

    def _fetch(self, url: str) -> requests.Response | None:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            return resp
        except requests.RequestException:
            return None

    def _parse(self, url: str, html: str) -> tuple[str, str, list[str]]:
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else url

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())

        links = []
        for a in soup.find_all("a", href=True):
            absolute = urljoin(url, a["href"]).split("#")[0]
            if absolute.startswith("http"):
                links.append(absolute)

        return title, text, links

    def crawl(self) -> list[Page]:
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(self.start_url, 0)])
        pages: list[Page] = []

        while queue and len(pages) < self.max_pages:
            url, depth = queue.popleft()
            if url in visited or depth > self.max_depth:
                continue
            visited.add(url)

            if not self._allowed(url):
                print(f"skip (robots.txt): {url}")
                continue

            print(f"fetching: {url}")
            resp = self._fetch(url)
            if resp is None:
                continue

            title, text, links = self._parse(url, resp.text)
            summary = summarize(text, title=title, model=self.model) if text else ""

            pages.append(Page(url=url, title=title, text=text, summary=summary, links=links))

            if depth < self.max_depth:
                for link in links:
                    if self._same_domain(link) and link not in visited:
                        queue.append((link, depth + 1))

            time.sleep(self.delay)

        return pages
