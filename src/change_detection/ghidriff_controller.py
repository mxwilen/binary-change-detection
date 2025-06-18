import os
import subprocess
import json
import difflib

from dotenv import load_dotenv

load_dotenv(".env")
GHIDRIFF_PROJECT_LOC = os.getenv("GHIDRIFF_PROJECT_LOC")
GHIDRIFF_JSON_OUTPUT_LOC = os.getenv("GHIDRIFF_JSON_OUTPUT_LOC")

from src.misc.FuncStatus import FuncStatus
from src.misc.FuncCollection import FuncCollection
from src.misc.FuncNode import FuncNode
from src.misc.DiffData import DiffData
from src.misc.GhidriffLog import GhidriffLog


def exec_ghidriff(old_dex, new_dex, 
                  log: GhidriffLog) -> GhidriffLog:

    print("\nStarting Ghidriff...")
    print("Analyzing pair: ", os.path.basename(old_dex))

    try:
        args = [
            "ghidriff",
            old_dex,
            new_dex,
            "-p",
            GHIDRIFF_PROJECT_LOC,
            "-n",
            f"{os.path.basename(old_dex)}-project",
            "--md-title",
            f"{os.path.basename(old_dex)}-report",
            "--force-diff",
        ]

        subprocess.run(args, check=True)
    except Exception as e:
        log.set_e(e)
    return log


def register_added_func(func: FuncNode, 
                        added_func_collection: FuncCollection, 
                        basename):
    old_code = []
    new_code = func["code"].splitlines()
    html_diff = difflib.HtmlDiff().make_file(old_code, new_code)

    mod_func_data = DiffData(
        old_sig=func["sig"],
        new_sig=func["sig"],
        original_diff_code=func["code"],
        diff_changes=None
    )

    added_func_collection.append_func(
        FuncNode(
            class_name=func["parent"],
            fullname=func["fullname"],
            name=func["name"],
            dex_file=basename,
            parent_func=func["calling"],
            child_func=func["called"],
            func_status=FuncStatus.ADDED,
            html_diff=html_diff,
            mod_func_data=mod_func_data,
            sig=func["sig"],
        )
    )

def register_deleted_func(func: FuncNode, 
                          deleted_func_collection: FuncCollection, 
                          basename):
    old_code = func["code"].splitlines()
    new_code = []
    html_diff = difflib.HtmlDiff().make_file(old_code, new_code)


    mod_func_data = DiffData(
        old_sig=func["sig"],
        new_sig=func["sig"],
        original_diff_code=func["code"],
        diff_changes=None
    )
    
    deleted_func_collection.append_func(
        FuncNode(
            class_name=func["parent"],
            fullname=func["fullname"],
            name=func["name"],
            dex_file=basename,
            parent_func=func["calling"],
            child_func=func["called"],
            func_status=FuncStatus.DELETED,
            html_diff=html_diff,
            mod_func_data=mod_func_data,
            sig=func["sig"],
        )
    )

def register_modified_func(func: FuncNode, 
                           modified_func_collection: FuncCollection, 
                           basename):
    diff_changes = {
        "code": False,
        "name": False,
        "fullname": False,
        "refcount": False,
        "length": False,
        "sig": False,
        "address": False,
        "calling": False,
        "called": False,
        "parent": False,
    }

    for diff in func["diff_type"]:
        if diff in diff_changes:
            diff_changes[diff] = True
    
    diff_changes_sorted = dict(
        sorted(diff_changes.items(), key=lambda item: item[1], reverse=True)
    )

    old_code = func["old"]["code"].splitlines()
    new_code = func["new"]["code"].splitlines()
    html_diff = difflib.HtmlDiff().make_file(old_code, new_code)

    mod_func_data = DiffData(
        old_sig=func["old"]["sig"],
        new_sig=func["new"]["sig"],
        original_diff_code=func["diff"],
        diff_changes=diff_changes_sorted,
    )

    modified_func_collection.append_func(
        FuncNode(
            class_name=func["new"]["parent"],
            fullname=func["new"]["fullname"],
            name=func["new"]["name"],
            dex_file=basename,
            parent_func=func["new"]["calling"],
            child_func=func["new"]["called"],
            func_status=FuncStatus.MODIFIED,
            html_diff=html_diff,
            mod_func_data=mod_func_data,
        )
    )


def extract_data_from_ghidriff(log: GhidriffLog, basename) -> GhidriffLog:

    # Open the JSON file and parse it
    with open(f"{GHIDRIFF_JSON_OUTPUT_LOC}/{basename}-{basename}.ghidriff.json", "r") as file:
        data = json.load(file)
    file.close()

    added_func_collection = FuncCollection(func_status=FuncStatus.ADDED)
    deleted_func_collection = FuncCollection(func_status=FuncStatus.DELETED)
    modified_func_collection = FuncCollection(func_status=FuncStatus.MODIFIED)
    
    for func in data["functions"]["added"]:
        if func is None: continue
        register_added_func(func, added_func_collection, basename)
    
    for func in data["functions"]["deleted"]:
        if func is None: continue
        
        # Ghidriff/Ghidra falsely sets some ADDED functions to DELETED because of how the 
        # memory address comparison is done. A workaround for this is to check if the 
        # function name can be found in the list of added symbols. If this is the case,
        # then add the function to the ADDED collection instead.
        if func["name"] in data.get("symbols", {}).get("added", []):
            print(f"* Changing status of method '{func['name']}' from DELETED to ADDED")
            register_added_func(func, added_func_collection, basename)
        else:
            register_deleted_func(func, deleted_func_collection, basename)

    for func in data["functions"]["modified"]:
        if func is None: continue
        register_modified_func(func, modified_func_collection, basename)

    log.set_symbols(data["symbols"])

    log.set_add_funcs(added_func_collection)
    log.set_del_funcs(deleted_func_collection)
    log.set_mod_funcs(modified_func_collection)

    return log
