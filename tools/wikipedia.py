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
def wikidata_tool(query: str) -> Dict[str, Any]:
    """
    Search Wikidata and return a human-readable summary.

    Returns:
    {
        "success": bool,
        "source": "wikidata",
        "title": "...",
        "content": "..."
    }
    """

    try:

        # ------------------------------------
        # First search
        # ------------------------------------
        r = session.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "format": "json",
                "limit": 1,
            },
            timeout=8,
        )

        results = r.json().get("search", [])

        # ------------------------------------
        # Retry with simplified query
        # ------------------------------------
        if not results:

            stopwords = {
                "host", "hosts", "hosting",
                "largest", "highest", "most",
                "capital", "population",
                "country", "city",
                "who", "what", "where",
                "is", "are", "the", "of"
            }

            simplified = " ".join(
                w for w in query.split()
                if w.lower() not in stopwords
            )

            if simplified and simplified != query:

                r = session.get(
                    "https://www.wikidata.org/w/api.php",
                    params={
                        "action": "wbsearchentities",
                        "search": simplified,
                        "language": "en",
                        "format": "json",
                        "limit": 1,
                    },
                    timeout=8,
                )

                results = r.json().get("search", [])

        if not results:
            return {
                "success": False,
                "source": "wikidata",
                "content": "No Wikidata entity found."
            }

        entity = results[0]
        entity_id = entity["id"]

        # ------------------------------------
        # Fetch full entity
        # ------------------------------------
        r = session.get(
            f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json",
            timeout=8,
        )

        entity_json = r.json()["entities"][entity_id]

        label = (
            entity_json
            .get("labels", {})
            .get("en", {})
            .get("value", entity.get("label", ""))
        )

        description = (
            entity_json
            .get("descriptions", {})
            .get("en", {})
            .get("value", "")
        )

        aliases = entity_json.get("aliases", {}).get("en", [])

        alias_text = ", ".join(
            a["value"] for a in aliases[:5]
        )

        claims = entity_json.get("claims", {})

        content = description

        if alias_text:
            content += f"\nAliases: {alias_text}"

        if claims:
            content += f"\nWikidata properties: {len(claims)}"

        return {
            "success": True,
            "source": "wikidata",
            "title": label,
            "content": content.strip(),
        }

    except Exception:
        logger.error(traceback.format_exc())

        return {
            "success": False,
            "source": "wikidata",
            "content": "Wikidata crashed."
        }