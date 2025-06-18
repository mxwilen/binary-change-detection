import re
import os

import plotly.express as px

from dotenv import load_dotenv

load_dotenv(".env")
CLASSIFICATION_OUTPUT = os.getenv("CLASSIFICATION_OUTPUT")
PIPELINE_JSON_PATH = os.getenv("PIPELINE_JSON_PATH")
PIPELINE_MAIN_HTML_REPORT = os.getenv("PIPELINE_MAIN_HTML_REPORT")
PIPELINE_JSON_PATH = os.getenv("PIPELINE_JSON_PATH")
OVERVIEW_OUTPUT = os.getenv("OVERVIEW_OUTPUT")
CRITICAL_CATEGORIES_OUTPUT = os.getenv("CRITICAL_CATEGORIES_OUTPUT")
NON_CRITICAL_CATEGORIES_OUTPUT = os.getenv("NON_CRITICAL_CATEGORIES_OUTPUT")

APK_LOC_V1 = os.getenv("APK_LOC_V1")
APK_LOC_V2 = os.getenv("APK_LOC_V2")

import re
v1 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V1).group(1)
v2 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V2).group(1)
VERSION_ID = f"{v1}-{v2}"

from src.misc.static import *


critical_changes = {
    "data_storage": 0,
    "file_write": 0,
    "logging_change": 0,
    "auth_change": 0,
    "error_handling": 0,
    "crypto_change": 0,
}

noncritical_changes = {
    "network_call": 0,
    "ui_update": 0,
    "text_manipulation": 0,
    "lib_func": 0,
}

stats = {
    "total changes": 0,
    "uncategorized": 0,
    "critical_changes": critical_changes,
    "noncritical_changes": noncritical_changes,
}

from src.categorization.static import Categories
from src.categorization.static import ClassificationType
from src.misc.FuncNode import FuncNode


def classify_func(func: FuncNode):
    """
    Classification main loop
    """

    # Avoid external library classes
    if func.is_library_function():
        noncritical_changes["lib_func"] += 1
        func.add_classification(Categories.C_LIB_FUNC)

    if is_synthetic_method(func.fullname):
        func.set_synthetic()
    if is_kotlin_synthetic_method(func.fullname):
        func.set_kotlin_synthetic()

    
    # Non-Critical categories
    if network_match := is_network_call(func.fullname):
        noncritical_changes["network_call"] += 1
        func.add_classification(Categories.C_NET_CALL)
        func.add_matched_keywords(network_match)

    if ui_match := is_ui_update(func.fullname):
        noncritical_changes["ui_update"] += 1
        func.add_classification(Categories.C_UI)
        func.add_matched_keywords(ui_match)

    if text_match := is_text_manipulation(func.fullname):
        noncritical_changes["text_manipulation"] += 1
        func.add_classification(Categories.C_TEXT_MAN)
        func.add_matched_keywords(text_match)
    

    # Critical categories
    # At the moment, only the critical categories have yaml files with words. 
    from src.categorization.matchers import (
        is_data_storage_change, 
        is_file_write, 
        is_logging_change, 
        is_error_handling, 
        is_auth_change, 
        is_crypto_change
    )

    if keywords := is_data_storage_change(func.fullname, func.diff_body):
        critical_changes["data_storage"] += 1
        func.add_critical_classification(Categories.C_DATA_STORAGE)
        func.add_matched_keywords(keywords)

    if keywords := is_file_write(func.fullname, func.diff_body):
        critical_changes["file_write"] += 1
        func.add_critical_classification(Categories.C_FILE_WRITE)
        func.add_matched_keywords(keywords)

    if keywords := is_logging_change(func.fullname, func.diff_body):
        critical_changes["logging_change"] += 1
        func.add_critical_classification(Categories.C_LOGGING)
        func.add_matched_keywords(keywords)

    if keywords := is_error_handling(func.fullname, func.diff_body):
        critical_changes["error_handling"] += 1
        func.add_critical_classification(Categories.C_ERROR)
        func.add_matched_keywords(keywords)

    if keywords := is_auth_change(func.fullname, func.diff_body):
        critical_changes["auth_change"] += 1
        func.add_critical_classification(Categories.C_AUTH)
        func.add_matched_keywords(keywords)

    if keywords := is_crypto_change(func.fullname, func.diff_body):
        critical_changes["crypto_change"] += 1
        func.add_critical_classification(Categories.C_CRYPTO)
        func.add_matched_keywords(keywords)

    # each function is set to uncategorized on init. if not changed => still uncategorized.
    if func.classification_type == ClassificationType.FLAG_UNCATEGORIZED:
        stats["uncategorized"] += 1



# === NON-CRITICAL CATEGORY MATCHERS ===
def is_network_call(full_name: str) -> list[str]:
    network_patterns = re.compile(
        r"(http|post|put|request|fetch|api|socket|connect|send|receive|sync|network)",
        re.IGNORECASE,
    )
    matches = network_patterns.findall(full_name)
    return matches


def is_ui_update(full_name: str) -> list[str]:
    ui_patterns = re.compile(
        r"(\bui\b|render|update|view|inflate|refresh|display|show|hide|toggle|setvisibility|animatingtoggle|font|scaffold|compact|windowsize|padding|fragment)",
        re.IGNORECASE,
    )
    matches = ui_patterns.findall(full_name)
    return matches


def is_text_manipulation(full_name: str) -> list[str]:
    text_patterns = re.compile(
        r"(spannable|text|string|replace|substring)", re.IGNORECASE
    )
    matches = text_patterns.findall(full_name)
    return matches


# === HELPERS ===
def is_synthetic_method(name: str) -> bool:
    """
    Detects compiler-generated synthetic methods and lambdas.
    """
    synthetic_patterns = re.compile(r"(\$\$|lambda\$|\$lambda|\$\d+)", re.IGNORECASE)
    return bool(synthetic_patterns.search(name))


def is_kotlin_synthetic_method(name: str) -> bool:
    """
    Detects Kotlin synthetic methods like copy$default.
    """
    kotlin_synthetic_patterns = re.compile(
        r"(copy\$default|create\$default|component\d+)", re.IGNORECASE
    )
    return bool(kotlin_synthetic_patterns.search(name))


def calls_critical_resources(line: str) -> bool:
    """
    Check if a line in the diff calls a critical resource.
    """
    critical_patterns = re.compile(
        r"(db|database|insert|delete|update|commit|query|log|transaction|rollback)",
        re.IGNORECASE,
    )
    return bool(critical_patterns.search(line))


def write_piecharts(nr_unique_critical: int, 
                    nr_unique_noncritical: int, 
                    nr_unique_uncategorized: int):
    
    stats["total changes"] = (
        sum(critical_changes.values())
        + sum(noncritical_changes.values())
        + stats["uncategorized"]
    )

    labels_categories_critical = list(critical_changes.keys())
    values_categories_critical = list(critical_changes.values())

    fig_categories = px.pie(
        names=labels_categories_critical,
        values=values_categories_critical,
        title=f"Critical changes ({nr_unique_critical})",
    )
    fig_categories.update_layout(paper_bgcolor="black", font=dict(color="white"))
    fig_categories.write_html(f"result/{VERSION_ID}/{CRITICAL_CATEGORIES_OUTPUT}")

    labels_categories_noncritical = list(noncritical_changes.keys())
    values_categories_noncritical = list(noncritical_changes.values())

    fig_categories = px.pie(
        names=labels_categories_noncritical,
        values=values_categories_noncritical,
        title=f"Noncritical changes ({nr_unique_noncritical})",
    )
    fig_categories.update_layout(paper_bgcolor="black", font=dict(color="white"))
    fig_categories.write_html(f"result/{VERSION_ID}/{NON_CRITICAL_CATEGORIES_OUTPUT}")


    # Below is only for unique changes
    labels_overview = ["Uncategorized", "Critical changes", "Non-critical changes"]
    values_overview = [
        nr_unique_uncategorized,
        nr_unique_critical,
        nr_unique_noncritical,
    ]

    total_unique_changes = nr_unique_critical + nr_unique_noncritical + nr_unique_uncategorized

    fig_overview = px.pie(
        names=labels_overview,
        values=values_overview,
        title=f"Distribution of unique changes ({total_unique_changes})",
    )
    fig_overview.update_layout(paper_bgcolor="black", font=dict(color="white"))
    fig_overview.write_html(f"result/{VERSION_ID}/{OVERVIEW_OUTPUT}")
