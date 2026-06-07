import logging
import traceback
import urllib.parse
from typing import Any, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# ------------------------------
# HTTP SESSION
# ------------------------------
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)
session.headers.update({
    "User-Agent": "fastapi-llm-agent/1.1",
    "Accept": "application/json",
})

# ------------------------------
# Wikipedia tool
# ------------------------------
def wikipedia_tool(query: str) -> Dict[str, Any]:
    try:
        r = session.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query, "format": "json"},
            timeout=8,
        )
        results = r.json().get("query", {}).get("search", [])
        if not results:
            return {"success": False, "source": "wikipedia", "content": "No results"}

        title = results[0]["title"]
        safe_title = urllib.parse.quote(title.replace(" ", "_"))
        summary = session.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}",
            timeout=8,
        )
        data = summary.json()
        return {
            "success": True,
            "source": "wikipedia",
            "title": title,
            "content": data.get("extract", ""),
        }
    except Exception:
        logger.error(traceback.format_exc())
        return {"success": False, "source": "wikipedia", "content": "Wikipedia crashed"}

# ------------------------------
# Wikidata tool (optional to move later)
# ------------------------------
def wikidata_tool(query: str) -> Dict[str, Any]:
    try:
        r = session.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "format": "json",
            },
            timeout=8,
        )
        results = r.json().get("search", [])
        if not results:
            return {"success": False, "source": "wikidata", "content": "No results"}

        item = results[0]
        return {
            "success": True,
            "source": "wikidata",
            "title": item.get("label"),
            "content": item.get("description", ""),
        }
    except Exception:
        logger.error(traceback.format_exc())
        return {"success": False, "source": "wikidata", "content": "Wikidata crashed"}