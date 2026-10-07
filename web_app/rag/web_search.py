"""
AirSense AI Web & Academic Search Engine
========================================
Combines DuckDuckGo search (via `ddgs`) and the arXiv API to provide real-time
internet grounding, developer documentation, sensor datasheets, and scientific
preprints when queries exceed local knowledge.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False


def search_web_ddg(query, max_results=3):
    """
    Performs DuckDuckGo web search to retrieve real-time internet knowledge.
    Returns list of dicts with title, body, href.
    """
    if not DDGS_AVAILABLE:
        return []
        
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        formatted = []
        for r in results:
            title = r.get('title', '').strip()
            body = r.get('body', '').strip()
            href = r.get('href', '').strip()
            if title and body:
                formatted.append({
                    "title": title,
                    "snippet": body,
                    "url": href,
                    "source": "Web (DuckDuckGo)"
                })
        return formatted
    except Exception as e:
        # Fallback quietly on network or rate limit
        return []


def search_arxiv(query, max_results=2):
    """
    Queries the arXiv API for academic preprints in atmospheric science,
    low-cost sensors, and machine learning calibration.
    """
    try:
        clean_q = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()
        encoded = urllib.parse.quote(clean_q)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={max_results}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AirSenseBot/2.0'})
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            results = []
            for entry in entries:
                title_el = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_el = entry.find('{http://www.w3.org/2005/Atom}summary')
                id_el = entry.find('{http://www.w3.org/2005/Atom}id')
                
                title = title_el.text.strip().replace('\n', ' ') if title_el is not None else "arXiv Preprint"
                summary = summary_el.text.strip().replace('\n', ' ')[:250] + "..." if summary_el is not None else ""
                link = id_el.text.strip() if id_el is not None else "https://arxiv.org"
                
                results.append({
                    "title": title,
                    "snippet": summary,
                    "url": link,
                    "source": "Academic Preprint (arXiv)"
                })
            return results
    except Exception:
        return []


def search_internet_and_arxiv(query, max_web=3, max_arxiv=2):
    """
    Executes a combined search across DuckDuckGo and arXiv.
    Returns aggregated citations.
    """
    results = []
    
    # 1. Web search
    web_res = search_web_ddg(query, max_results=max_web)
    results.extend(web_res)
    
    # 2. arXiv academic search if query has research/academic nature
    q_lower = query.lower()
    if any(k in q_lower for k in ["paper", "study", "research", "algorithm", "calibration", "model", "accuracy", "literature", "sensor"]):
        arxiv_res = search_arxiv(query, max_results=max_arxiv)
        results.extend(arxiv_res)
        
    return results


def format_search_results_for_prompt(results):
    """
    Formats search results into a clean markdown block for LLM prompt context.
    """
    if not results:
        return ""
        
    lines = ["=== REAL-TIME INTERNET & ACADEMIC SEARCH KNOWLEDGE ==="]
    for i, r in enumerate(results):
        lines.append(f"[{i+1}] {r['title']} ({r['source']})")
        lines.append(f"    URL: {r['url']}")
        lines.append(f"    Excerpt: {r['snippet']}")
    return "\n".join(lines)
