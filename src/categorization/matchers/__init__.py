"""
matchers - one lazy-loaded engine, many categories
-------------------------------------------------
Public helpers:
    is_data_storage_change(name, diff)  → List[str]
    is_file_write(name, diff)          → …
    …etc…

* All keyword files live in the same folder, one YAML per category.
* Regexes are compiled once and cached with @lru_cache.
* Duplicate hits are removed; order of first appearance is preserved.
"""

from __future__ import annotations
import re, yaml, importlib.resources as pkg, functools
from pathlib import Path
from typing import List, Dict, Sequence

# ── INTERNAL UTILS ────────────────────────────────────────────────────

def _load_yaml(name: str) -> Dict[str, Sequence[str]]:
    """Read `<name>.yml` from this package and return its dict."""
    with pkg.files(__name__).joinpath(f"{name}.yml").open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

def _build_regexes(words: Sequence[str]) -> re.Pattern:
    """Return 2-branch pattern for stand-alone camel/snake segment detection."""
    joined = "|".join(map(re.escape, words))
    return re.compile(
        rf"(?<![A-Za-z])(?:{joined})(?![a-z])|"
        rf"(?<=[^A-Za-z])(?:{joined})(?=[A-Z])",
        re.IGNORECASE,
    )

@functools.lru_cache(maxsize=None)
def _category_cfg(category: str):
    """Load YAML, build compiled regexes, and memorise result."""
    cfg = _load_yaml(category)
    return {
        "seg_re":  _build_regexes(cfg.get("standalone", [])),
        "strong":  re.compile(rf"({'|'.join(map(re.escape, cfg.get('strong', [])))})",
                              re.IGNORECASE) if cfg.get("strong") else None,
        "weak":    re.compile(rf"({'|'.join(map(re.escape, cfg.get('weak', [])))})",
                              re.IGNORECASE) if cfg.get("weak") else None,
    }

def _run_category(category: str, name: str, diff: str) -> List[str]:
    """Generic runner that applies all regexes for *category* to both texts."""
    cfg = _category_cfg(category)

    hits = (
        cfg["seg_re"].findall(name) +
        cfg["seg_re"].findall(diff)
    )
    if cfg["strong"]:
        hits += cfg["strong"].findall(name) + cfg["strong"].findall(diff)
    if cfg["weak"]:
        hits += cfg["weak"].findall(name) + cfg["weak"].findall(diff)

    # deduplicate while keeping first‑seen order
    return list(dict.fromkeys(hits))


# ── PUBLIC API ────────────────────────────────────────────────────────

def is_data_storage_change(full_name: str, diff_body: str) -> List[str]:
    return _run_category("data_storage", full_name, diff_body)

def is_file_write(full_name: str, diff_body: str) -> List[str]:
    return _run_category("file_write", full_name, diff_body)

def is_logging_change(full_name: str, diff_body: str) -> List[str]:
    return _run_category("logging", full_name, diff_body)

def is_error_handling(full_name: str, diff_body: str) -> List[str]:
    return _run_category("error_handling", full_name, diff_body)

def is_auth_change(full_name: str, diff_body: str) -> List[str]:
    return _run_category("auth", full_name, diff_body)

def is_crypto_change(full_name: str, diff_body: str) -> List[str]:
    return _run_category("crypto", full_name, diff_body)


