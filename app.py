"""Web UI for the crawler. Streams crawl progress to the browser over SSE."""

import json

from flask import Flask, Response, request

from crawler import Crawler

app = Flask(__name__, static_folder="static", static_url_path="")


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/crawl")
def crawl():
    url = request.args.get("url", "").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    max_pages = max(1, min(int(request.args.get("max_pages", 10)), 50))
    max_depth = max(0, min(int(request.args.get("max_depth", 2)), 5))

    def event(name: str, data) -> str:
        return f"event: {name}\ndata: {json.dumps(data)}\n\n"

    def stream():
        crawler = Crawler(url, max_pages=max_pages, max_depth=max_depth)
        count = 0
        try:
            for kind, item in crawler.crawl_iter():
                if kind == "fetching":
                    yield event("fetching", {"url": item})
                else:
                    count += 1
                    yield event("page", {
                        "url": item.url,
                        "title": item.title,
                        "summary": item.summary,
                        "depth": item.depth,
                        "num_links": len(item.links),
                    })
        except Exception as exc:
            yield event("error", {"message": str(exc)})
            return
        yield event("done", {"count": count})

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
