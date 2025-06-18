import importlib.resources as pkg
import yaml
from typing import Set

def load_all_weak_words() -> Set[str]:
    """
    Walk through every *.yml file inside "matchers" and return the union
    of all `weak:` entries (case-folded).
    """
    words: set[str] = set()

    for yml in pkg.files("src.categorization.matchers").iterdir():
        if yml.suffix != ".yml":
            continue
        with yml.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            for w in data.get("weak", []):
                words.add(str(w).lower())

    return words