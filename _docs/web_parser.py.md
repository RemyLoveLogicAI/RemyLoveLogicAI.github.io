<details>
<summary>Documentation Metadata (click to expand)</summary>

```json
{
  "doc_type": "file_overview",
  "file_path": "web_parser.py",
  "source_hash": "5ac010455ac8e8b13d13dd8a6437142a26407f828c2623cb5312dbcdb4081d49",
  "last_updated": "2026-02-26T05:55:28.606692+00:00",
  "tokens_used": 7170,
  "complexity_score": 3,
  "estimated_review_time_minutes": 10,
  "external_dependencies": [
    "requests",
    "bs4"
  ]
}
```

</details>

[Documentation Home](README.md) > **web_parser**

---

# web_parser.py

> **File:** `web_parser.py`

![Complexity: Low](https://img.shields.io/badge/Complexity-Low-green) ![Review Time: 10min](https://img.shields.io/badge/Review_Time-10min-blue)

## 📑 Table of Contents


- [Overview](#overview)
- [Dependencies](#dependencies)
- [Architecture Notes](#architecture-notes)
- [Usage Examples](#usage-examples)
- [Maintenance Notes](#maintenance-notes)
- [Functions and Classes](#functions-and-classes)

---

## Overview

This module centers on a single, re-usable scraping/parsing helper: fetch_and_parse_website(url: str, session: requests.Session = None) -> dict. It creates and reuses a module-level requests.Session named _session (with a custom User-Agent) for connection pooling and reduced TCP overhead. The function performs an HTTP GET (10s timeout), raises on bad responses, parses the response with BeautifulSoup (preferring the 'lxml' parser and falling back to the built-in 'html.parser'), and assembles a result dictionary containing extracted human-readable text, a list of absolute http(s) links, a list of identified YouTube video records, and the BeautifulSoup object for any further downstream processing.

The file contains lightweight heuristics and fallbacks to improve extraction quality: it prefers the <main> element for text extraction, otherwise iterates over ['p', 'article', 'div'] elements while skipping elements whose classes or ids intersect with the _BOILERPLATE_TERMS set (header, footer, nav, menu, sidebar, advertisement, banner, popup). If that still yields no text, it strips <script> and <style> tags and extracts all text from the document. Link extraction intentionally filters out non-absolute hrefs (only keeps URLs starting with 'http://' or 'https://') and performs a simple substring check to identify YouTube links (matching 'youtube.com/watch?v=' or 'youtu.be/'). The module also includes a __main__ block demonstrating basic usage by fetching two example URLs and printing snippets of the results.

## Dependencies

### External Dependencies

| Module | Usage |
| --- | --- |
| `requests` | Imported via 'import requests'. Used to create and reuse a requests.Session() in the module-level _session, to perform HTTP GET requests (s.get(url, timeout=10)), and to reference requests.exceptions.RequestException for error handling. |
| `bs4` | Imported via 'from bs4 import BeautifulSoup'. The BeautifulSoup class is used to parse response.content with 'lxml' if available or fall back to 'html.parser'. The resulting soup is used for find/find_all, get_text, decompose (for removing script/style), and is returned in the output dict. |

## 📁 Directory

This file is part of the **_docs** directory. View the [directory index](_docs/README.md) to see all files in this module.

## Architecture Notes

- Connection pooling: A module-level requests.Session named _session is created and its headers updated with a custom User-Agent to reduce per-request TCP overhead and identify the scraper.
- Parsing strategy: The implementation prefers the <main> tag for high-quality content extraction, then falls back to iterating ['p','article','div'] while skipping elements whose class or id contains common boilerplate terms. Final fallback strips script/style tags and takes the entire document text.
- Link extraction and filtering: Only absolute links (href starting with 'http://' or 'https://') are included. Relative links are intentionally ignored, reducing noisy or broken links but requiring callers to resolve relative URLs themselves if needed.
- YouTube detection: Implemented via simple substring matching ('youtube.com/watch?v=' or 'youtu.be/'), which catches common external video links but will not detect embedded iframe players that do not use those substrings in <a> hrefs.
- Error handling: Network and HTTP errors are caught by wrapping requests in try/except for requests.exceptions.RequestException; on error the function prints an error message and returns None rather than raising. This keeps callers simple but requires them to check for None.
- Synchronous/blocking: The design uses blocking requests; for high-throughput or concurrent scraping consider an async redesign (httpx or aiohttp) or a worker queue.

## Usage Examples

### Programmatic page summarization or link extraction

Call fetch_and_parse_website('https://example.com') (optionally passing a custom requests.Session) to retrieve a dictionary result. On success the function returns a dict with keys: 'text' (string containing extracted human-readable content), 'links' (list of {"text","href"} for absolute anchors), 'youtube_videos' (list of dicts with 'url','title','retrieved_from_url'), and 'soup' (BeautifulSoup object). Callers must check for None (returned when a RequestException occurs). Because only absolute http(s) links are collected, callers wanting to include relative URLs should resolve them against the page URL before use.

### Command-line/manual testing (demonstrated in __main__ block)

Running the file directly executes the __main__ block which defines two test URLs, calls fetch_and_parse_website for each, and prints a short snippet of the extracted text, first three links, and any detected YouTube videos. This demonstrates typical usage and quick verification without embedding the module in a larger application.

## Maintenance Notes

- Performance: Parsing large pages and returning the full BeautifulSoup object can be memory-heavy. If result objects are serialized or passed between processes, avoid including 'soup' or convert extracted data to plain structures first.
- Dependencies and parser speed: The code prefers the 'lxml' parser (faster) but falls back to 'html.parser'. Ensure 'lxml' is installed in environments where performance matters (pip install lxml).
- Edge cases: The boilerplate filtering uses simple substring membership on class lists and element ids—this may both over-filter and under-filter on some sites. Developers should adjust _BOILERPLATE_TERMS or the heuristics for site-specific scraping.
- Link handling: Only absolute links are returned. If the calling code needs relative links, implement URL joining (e.g., urllib.parse.urljoin) before or after calling this function.
- Testing: Unit tests should mock network calls (requests.Session.get) and assert behavior for successful responses, non-2xx responses, timeouts, content parsed with and without <main>, and pages with/without YouTube links. Also test fallback to 'html.parser' by simulating an lxml import failure.
- Future improvements: Consider adding explicit parser parameter, optional automatic resolution of relative links, rate-limiting, retries with backoff, and an async variant using httpx or aiohttp for concurrent scraping.

---

## Navigation

**↑ Parent Directory:** [Go up](_docs/README.md)

---

*This documentation was automatically generated by AI ([Woden DocBot](https://github.com/marketplace/ai-document-creator)) and may contain errors. It is the responsibility of the user to validate the accuracy and completeness of this documentation.*
