from src.categorization.static import Categories
from src.categorization.static import ClassificationType
from src.misc.FuncNode import FuncNode

from src.categorization.helpers import load_all_weak_words

# Eg. functions names from commonly used libraries
WEAK_WORDS = load_all_weak_words()

def evaluate_func(func: FuncNode, temp: list[list]) -> None:
    """
    The evaluation score reflects how many category and keyword “hits” 
    a function receives. A higher score flags functions that exhibit 
    a wider variety of detected operations—making it easy to sort and 
    surface the most interesting ones first.

    The score has not cap.
    """

    raw_score = 0

    # Classification weight
    if func.classification_type is ClassificationType.FLAG_CRITICAL:
        raw_score += len(func.critical_classifications)
    elif func.classification_type is ClassificationType.FLAG_GENERAL:
        raw_score += len(func.classifications)

    # Keyword bonus
    for kw in func.get_matched_keywords():
        if kw.lower() not in WEAK_WORDS:
            raw_score += 1          # each keyword add 1 pt

    func.eval_rating = raw_score
    temp.append([list(func.get_matched_keywords()),
                 list(func.get_classifications()),
                 raw_score])
    