from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from http.client import IncompleteRead
from math import ceil
from typing import Any

from .schemas import EvidenceDoc

USER_AGENT = "BioResearch-Agent/0.1 public-safe literature workflow"


def search_live_references(query: str, *, top_k: int = 6) -> tuple[EvidenceDoc, ...]:
    """Search public PubMed, arXiv, and bioRxiv metadata and normalize results."""

    per_source = max(1, ceil(top_k / 3))
    docs: list[EvidenceDoc] = []
    source_errors: list[EvidenceDoc] = []
    for source, searcher in (
        ("pubmed", search_pubmed),
        ("arxiv", search_arxiv),
        ("biorxiv", search_biorxiv),
    ):
        try:
            docs.extend(_search_with_fallback(searcher, query, limit=per_source))
        except Exception as exc:
            source_errors.append(
                EvidenceDoc(
                    doc_id=f"{source}-live-error",
                    title=f"{source} live search failed",
                    source=f"{source}-live-error",
                    abstract=f"{type(exc).__name__}: {exc}",
                    tags=("live-source-error", source),
                )
            )
    ranked = _dedupe(docs)
    return tuple((ranked or source_errors)[:top_k])


def search_pubmed(query: str, *, limit: int = 5) -> tuple[EvidenceDoc, ...]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(limit),
        "sort": "relevance",
        "tool": "bioresearch_agent",
    }
    email = os.environ.get("NCBI_EMAIL")
    api_key = os.environ.get("NCBI_API_KEY")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    payload = _get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params)
    pmids = payload.get("esearchresult", {}).get("idlist", [])[:limit]
    if not pmids:
        return ()
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "tool": "bioresearch_agent",
    }
    if email:
        fetch_params["email"] = email
    if api_key:
        fetch_params["api_key"] = api_key
    xml_text = _get_text("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", fetch_params)
    root = ET.fromstring(xml_text)
    docs = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article.find(".//PMID"))
        title = _join_text(article.findall(".//ArticleTitle")) or f"PubMed article {pmid}"
        abstract = _join_text(article.findall(".//AbstractText"))
        journal = _join_text(article.findall(".//Journal/Title"))
        doi = ""
        for article_id in article.findall(".//ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = _text(article_id)
                break
        year = _safe_int(_text(article.find(".//PubDate/Year")))
        tags = tuple(item for item in ("pubmed", journal, f"doi:{doi}" if doi else "") if item)
        docs.append(
            EvidenceDoc(
                doc_id=f"PMID:{pmid}",
                source="pubmed-live",
                source_id=pmid,
                title=_clean(title),
                abstract=_clean(abstract),
                tags=tags,
                year=year,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                doi=doi,
            )
        )
    return tuple(docs)


def search_arxiv(query: str, *, limit: int = 5) -> tuple[EvidenceDoc, ...]:
    params = {
        "search_query": f"all:{query}",
        "start": "0",
        "max_results": str(limit),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    xml_text = _get_text("https://export.arxiv.org/api/query", params)
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    docs = []
    for entry in root.findall("atom:entry", ns):
        arxiv_id = _text(entry.find("atom:id", ns)).rsplit("/", 1)[-1]
        title = _text(entry.find("atom:title", ns))
        abstract = _text(entry.find("atom:summary", ns))
        published = _text(entry.find("atom:published", ns))
        year = _safe_int(published[:4])
        doi = _text(entry.find("arxiv:doi", {"arxiv": "http://arxiv.org/schemas/atom"}))
        category = ""
        category_node = entry.find("atom:category", ns)
        if category_node is not None:
            category = category_node.attrib.get("term", "")
        docs.append(
            EvidenceDoc(
                doc_id=f"arXiv:{arxiv_id}",
                source="arxiv-live",
                source_id=arxiv_id,
                title=_clean(title),
                abstract=_clean(abstract),
                tags=tuple(item for item in ("arxiv", category, f"doi:{doi}" if doi else "") if item),
                year=year,
                url=f"https://arxiv.org/abs/{arxiv_id}",
                doi=doi,
            )
        )
    time.sleep(3.1)
    return tuple(docs)


def search_biorxiv(query: str, *, limit: int = 5) -> tuple[EvidenceDoc, ...]:
    today = date.today()
    start = today - timedelta(days=180)
    params: dict[str, str] = {}
    url = f"https://api.biorxiv.org/details/biorxiv/{start.isoformat()}/{today.isoformat()}/0"
    payload = _get_json(url, params)
    query_terms = _tokens(query)
    docs = []
    for item in payload.get("collection", []):
        title = _clean(str(item.get("title", "")))
        abstract = _clean(str(item.get("abstract", "")))
        haystack = _tokens(" ".join([title, abstract, str(item.get("category", ""))]))
        if query_terms and not (query_terms & haystack):
            continue
        doi = str(item.get("doi", ""))
        published = str(item.get("date", ""))
        year = _safe_int(published[:4])
        url_value = f"https://doi.org/{doi}" if doi else str(item.get("server", ""))
        category = str(item.get("category", ""))
        docs.append(
            EvidenceDoc(
                doc_id=f"bioRxiv:{doi or title[:40]}",
                source="biorxiv-live",
                source_id=doi,
                title=title or "bioRxiv preprint",
                abstract=abstract,
                tags=tuple(tag for tag in ("biorxiv", category, f"doi:{doi}" if doi else "") if tag),
                year=year,
                url=url_value,
                doi=doi,
            )
        )
        if len(docs) >= limit:
            break
    return tuple(docs)


def _get_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    return json.loads(_get_text(url, params))


def _get_text(url: str, params: dict[str, str]) -> str:
    encoded = urllib.parse.urlencode(params)
    full_url = f"{url}?{encoded}" if encoded else url
    request = urllib.request.Request(full_url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return response.read().decode("utf-8", errors="replace")
        except IncompleteRead as exc:
            last_error = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"GET failed after retries: {full_url}") from last_error


def _search_with_fallback(searcher: Any, query: str, *, limit: int) -> tuple[EvidenceDoc, ...]:
    for candidate in _fallback_queries(query):
        docs = searcher(candidate, limit=limit)
        if docs:
            return docs
    return ()


def _fallback_queries(query: str) -> tuple[str, ...]:
    tokens = re.findall(r"[A-Za-z0-9+-]+", query)
    stop = {
        "rag",
        "dataset",
        "datasets",
        "workflow",
        "workflows",
        "biomedical",
        "literature",
        "citation",
        "citations",
        "entity",
        "extraction",
        "method",
        "methods",
        "agent",
        "agents",
    }
    trimmed = " ".join(token for token in tokens if token.lower() not in stop)
    compact = " ".join(tokens[:4])
    candidates = [query, trimmed, compact]
    deduped = []
    for candidate in candidates:
        cleaned = _clean(candidate)
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return tuple(deduped)


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def _join_text(nodes: list[ET.Element]) -> str:
    return " ".join(_text(node) for node in nodes if _text(node))


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _safe_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_+-]{2,}", text.lower()))


def _dedupe(docs: list[EvidenceDoc]) -> list[EvidenceDoc]:
    seen: set[str] = set()
    deduped: list[EvidenceDoc] = []
    for doc in docs:
        key = (doc.doi or doc.source_id or doc.title).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(doc)
    return deduped
