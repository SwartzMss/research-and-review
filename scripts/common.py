"""Shared validation and loading for Research & Review (stdlib only)."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

KINDS = {"article", "report", "video", "post"}
CREDIBILITY = {"high", "medium", "low", "unknown"}
RIGHTS = {"licensed", "permission-required", "unknown", "not-applicable"}
STATUSES = {"verified", "reported", "disputed", "unverified"}
DECISIONS = {"pending", "research", "visual", "exclude"}


def valid_url(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_catalog(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    require(isinstance(data, dict), "catalog must be an object")
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1, "schema_version must be 1")
    require(isinstance(data.get("topic"), str) and data["topic"].strip(), "missing topic")
    require(isinstance(data.get("sources"), list), "sources must be an array")

    ids = set()
    for index, source in enumerate(data["sources"]):
        name = "sources[" + str(index) + "]"
        require(isinstance(source, dict), name + " must be an object")
        sid = source.get("id")
        require(isinstance(sid, str) and re.fullmatch(r"[A-Za-z0-9_-]+", sid), name + ".id invalid")
        require(sid not in ids, "duplicate source id: " + sid)
        ids.add(sid)
        require(source.get("kind") in KINDS, sid + ": invalid kind")
        for field in ("title", "summary", "evaluation"):
            require(isinstance(source.get(field), str) and source[field].strip(), sid + ": missing " + field)
        require(valid_url(source.get("url")), sid + ": invalid source URL")
        require(type(source.get("relevance")) is int and 1 <= source["relevance"] <= 5, sid + ": relevance must be integer 1-5")
        require(source.get("credibility") in CREDIBILITY, sid + ": invalid credibility")
        require(source.get("rights") in RIGHTS, sid + ": invalid rights")
        if "thumbnail_url" in source:
            require(valid_url(source["thumbnail_url"]), sid + ": invalid thumbnail URL")
        if "preview_path" in source:
            preview = source["preview_path"]
            require(isinstance(preview, str) and preview.strip(), sid + ": invalid preview_path")
            p = Path(preview)
            require(not p.is_absolute() and ".." not in p.parts and not preview.startswith(("/", "\\")) and ":" not in preview and "\\" not in preview, sid + ": preview_path must be safe relative path")
        claims = source.get("claims", [])
        require(isinstance(claims, list), sid + ": claims must be an array")
        for claim in claims:
            require(isinstance(claim, dict) and isinstance(claim.get("text"), str) and claim["text"].strip(), sid + ": invalid claim")
            require(claim.get("status") in STATUSES, sid + ": invalid claim status")
            evidence = claim.get("evidence_urls", [])
            require(isinstance(evidence, list) and all(valid_url(u) for u in evidence), sid + ": invalid evidence URLs")
            if "at_seconds" in claim:
                require(type(claim["at_seconds"]) in (float, int) and claim["at_seconds"] >= 0, sid + ": invalid claim time")
            if claim["status"] == "verified":
                require(len(evidence) > 0, sid + ": verified claim requires evidence_urls")
        clips = source.get("clips", [])
        require(isinstance(clips, list), sid + ": clips must be an array")
        require(not clips or source["kind"] == "video", sid + ": only videos can have clips")
        for clip in clips:
            require(isinstance(clip, dict), sid + ": invalid clip")
            a, b = clip.get("start"), clip.get("end")
            require(type(a) in (int, float) and type(b) in (int, float) and 0 <= a < b, sid + ": clip end must exceed start")
            require(isinstance(clip.get("description"), str) and clip["description"].strip(), sid + ": missing clip description")
    return data


def load_selection(path, catalog):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    require(isinstance(data, dict), "selection must be an object")
    require(data.get("schema_version") == 1, "selection schema_version must be 1")
    require(data.get("topic") == catalog["topic"], "selection topic does not match catalog")
    require(isinstance(data.get("decisions"), list), "decisions must be array")
    valid_ids = {source["id"]: source for source in catalog["sources"]}
    seen = set()
    for item in data["decisions"]:
        require(isinstance(item, dict), "invalid decision entry")
        sid = item.get("source_id")
        require(isinstance(sid, str) and sid in valid_ids, "unknown source_id: " + str(sid))
        require(sid not in seen, "duplicate decision: " + sid)
        seen.add(sid)
        require(item.get("decision") in DECISIONS, sid + ": invalid decision")
        require(not (item["decision"] == "visual" and valid_ids[sid]["kind"] != "video"), sid + ": only videos can be visual")
        require(isinstance(item.get("note"), str), sid + ": note must be a string")
    return data
