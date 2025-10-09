"""Scrape GradCafe applicant data."""

# pylint: disable=too-many-locals, too-many-branches, invalid-name
# pylint: disable=no-member

from __future__ import annotations
import os, json, re
from typing import List, Dict, Tuple, Optional

DATA_FILE = os.getenv("DATA_FILE", "/app/data/full_out.jsonl")

def _to_float(v):
    if v in (None, "", "N/A"):
        return None
    try:
        return float(v)
    except Exception:
        m = re.search(r"[-+]?\d*\.?\d+", str(v))
        return float(m.group()) if m else None

def _sort_key(entry: Dict) -> Optional[str]:
    """
    Produce a monotonic-ish sort key for watermarking.
    Prefer ISO-ish date strings in `date_added`; else fall back to numeric id parsed from URL.
    Return None if neither is available.
    """
    date = entry.get("date_added")
    if isinstance(date, str) and re.match(r"^\d{4}-\d{2}-\d{2}", date.strip()):
        # Good ISO-ish date (YYYY-MM-DD...) — safe for lexicographic compare
        return date.strip()

    # Fallback: extract numeric id from url .../result/123456?...
    url = entry.get("url") or ""
    m = re.search(r"/result/(\d+)", url)
    if m:
        # Left-pad so lexicographic compare works
        return f"id:{int(m.group(1)):012d}"
    return None

def _normalize(entry: Dict) -> Dict:
    """Map raw JSONL -> applicants table schema."""
    return {
        "program": entry.get("program"),
        "degree": entry.get("degree_type"),
        "comments": entry.get("comments"),
        "date_added": entry.get("date_added"),
        "status": entry.get("status"),
        "url": entry.get("url"),
        "gpa": _to_float(entry.get("GPA")),
        "gre": _to_float(entry.get("GRE_G")),
        "gre_v": _to_float(entry.get("GRE_V")),
        "gre_aw": _to_float(entry.get("GRE_AW")),
        "term": entry.get("term"),
        "us_or_international": entry.get("US/International"),
        "llm_generated_program": entry.get("llm-generated-program"),
        "llm_generated_university": entry.get("llm-generated-university"),
        "university": entry.get("university"),
    }

def run_scraper(since: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
    """
    Incremental loader:
      - Reads /app/data/full_out.jsonl
      - Computes sort_key per entry
      - Returns only rows with sort_key > since (string compare)
      - Returns (rows, max_seen) where max_seen is the maximum sort_key observed
    Notes:
      - If since is None/empty → return EVERYTHING (first run).
      - We compare strings; ensure both since and keys are comparable strings (see _sort_key).
    """
    rows: List[Dict] = []
    max_seen: Optional[str] = since

    # Normalize since to string (or None)
    since_key = str(since) if since else None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            key = _sort_key(entry)
            if key is None:
                # if we can't create a key, treat as new (include) so we don't miss data
                include = True if since_key is None else True
            else:
                include = (since_key is None) or (key > since_key)

            if include:
                rows.append(_normalize(entry))
                if key is not None and (max_seen is None or key > max_seen):
                    max_seen = key

    return rows, max_seen
