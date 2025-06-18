import os
import zipfile
import glob
import time

from dotenv import load_dotenv
load_dotenv(".env")
APK_LOC_V1 = os.getenv("APK_LOC_V1")
APK_LOC_V2 = os.getenv("APK_LOC_V2")

import re
v1 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V1).group(1)
v2 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V2).group(1)
VERSION_ID = f"{v1}-{v2}"

# Ensure the output directory exists
os.makedirs(f"result/{VERSION_ID}", exist_ok=True)

GHIDRA_INSTALL_DIR = os.getenv("GHIDRA_INSTALL_DIR")
GHIDRIFF_PROJECT_LOC = os.getenv("GHIDRIFF_PROJECT_LOC")
GHIDRIFF_OUTPUT_LOC = os.getenv("GHIDRIFF_OUTPUT_LOC")
GHIDRIFF_JSON_OUTPUT_LOC = os.getenv("GHIDRIFF_JSON_OUTPUT_LOC")
CLASSIFICATION_OUTPUT = os.getenv("CLASSIFICATION_OUTPUT")
PIPELINE_JSON_PATH = os.getenv("PIPELINE_JSON_PATH")
PIPELINE_MAIN_HTML_REPORT = os.getenv("PIPELINE_MAIN_HTML_REPORT")


#############################
#         HELPERS           #
#############################
def unpack_apk(apk_path, output_dir):
    """Unpack APK if it hasn't been unpacked yet."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.listdir(output_dir):
        with zipfile.ZipFile(apk_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"APK unpacked at {output_dir}")
    else:
        print(f"APK has already been unpacked at {output_dir}, skipping unpacking.")


#############################
#         MAIN LOOP         #
#############################
def main():
    apk1 = APK_LOC_V1
    apk2 = APK_LOC_V2

    unpack_dir1 = f"output/unpacked_{os.path.splitext(os.path.basename(apk1))[0]}"
    unpack_dir2 = f"output/unpacked_{os.path.splitext(os.path.basename(apk2))[0]}"

    unpack_apk(apk1, unpack_dir1)
    unpack_apk(apk2, unpack_dir2)

    dex_files1 = glob.glob(os.path.join(unpack_dir1, "*.dex"))
    dex_files2 = glob.glob(os.path.join(unpack_dir2, "*.dex"))

    #############################
    #      CHANGE DETECTION     #
    #############################

    from src.change_detection.ghidriff_controller import exec_ghidriff
    from src.change_detection.ghidriff_controller import extract_data_from_ghidriff
    from src.misc.GhidriffLog import GhidriffLog
    from src.misc.static import CLI_GREEN, CLI_RED, CLI_YELLOW, CLI_NC
    from src.misc.static import PYTHON_LINE_BREAK

    logs = []

    print(PYTHON_LINE_BREAK)
    for dex_v1, dex_v2 in zip(sorted(dex_files1), sorted(dex_files2)):
        basename = os.path.basename(dex_v1)

        print(f"{CLI_YELLOW}\nRUNNING GHIDRIFF ON {basename}...{CLI_NC}")

        log = GhidriffLog(basename)
        try:
            log = exec_ghidriff(dex_v1, dex_v2, log)
            log = extract_data_from_ghidriff(log, basename=basename)
            print(
                f"{CLI_GREEN}COMPLETE{CLI_NC} - Analysis and export completed for files {basename}"
            )
        except Exception as e:
            print(f"{CLI_RED}ERROR DURING ANALYSIS{CLI_NC}\n - {str(e)}")
            log.set_e(f"ERROR DURING ANALYSIS - {''.join(str(e))}")

        logs.append(log)

    print(f"{CLI_GREEN}\n\nALL GHIDRIFF EXECUTIONS DONE.{CLI_NC}")

    #############################
    #       CLASSIFICATION      #
    #############################

    from src.categorization.categorization import classify_func
    from src.categorization.metadata_registration import register_classification_metadata

    print(PYTHON_LINE_BREAK)
    for log in logs:

        try:
            print(
                f"\n{CLI_YELLOW}PERFORMING CLASSIFICATION ON {log.dex_file}...{CLI_NC}"
            )

            # Added funcs
            collection = log.get_add_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    classify_func(func)
                    register_classification_metadata(func, collection)

            # Deleted funcs
            collection = log.get_del_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    classify_func(func)
                    register_classification_metadata(func, collection)

            # Modified funcs
            collection = log.get_mod_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    classify_func(func)
                    register_classification_metadata(func, collection)

            print(f"{CLI_GREEN}CLASSIFICATION DONE.{CLI_NC}")

        except Exception as e:
            print(f"{CLI_RED}ERROR DURING CLASSIFICATION{CLI_NC}\n - {str(e)}")
            log.set_e(
                f"ERROR DURING CLASSIFICATION - {''.join(str(e))}"
            )

    #############################
    #         EVALUATION        #
    #############################

    from src.evaluation.eval import evaluate_func

    print(PYTHON_LINE_BREAK)
    temp = []
    for log in logs:
        try:
            print(f"\n{CLI_YELLOW}PERFORMING EVALUATION ON {log.dex_file}...{CLI_NC}")

            # Added
            collection = log.get_add_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    evaluate_func(func, temp)

            # Modified
            collection = log.get_mod_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    evaluate_func(func, temp)

            # Deleted
            collection = log.get_del_func_collection()
            if collection is not None:
                for func in collection.get_list():
                    evaluate_func(func, temp)
            
            print(f"{CLI_GREEN}EVALUATION DONE.{CLI_NC}")

        except Exception as e:
            print(f"{CLI_RED}ERROR DURING EVALUATION{CLI_NC}\n - {str(e)}")
            log.set_e(f"ERROR DURING EVALUATION\n - {''.join(str(e))}")

    #############################
    #           RESULT          #
    #############################

    import json
    from src.categorization.categorization import write_piecharts
    from src.misc.report_generation import generate_html_report
    from datetime import datetime

    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            return str(obj)  # Fallback: just convert to string

    all_funcs = {}
    tot_unique_critical_funcs      = 0
    tot_unique_noncritical_funcs   = 0
    tot_unique_uncategorized_funcs = 0
    
    for log in logs:

        try:

            # Added
            collection = log.get_add_func_collection()

            tot_unique_critical_funcs      += collection.get_amount_of_unique_critical_funcs()
            tot_unique_noncritical_funcs   += collection.get_amount_of_unique_noncritical_funcs()
            tot_unique_uncategorized_funcs += collection.get_amount_of_unique_uncategorized_funcs()

            for func in collection.get_list():
                func_json = func.__repr__()
                all_funcs.update(func_json)

            # Deleted
            collection = log.get_del_func_collection()

            tot_unique_critical_funcs      += collection.get_amount_of_unique_critical_funcs()
            tot_unique_noncritical_funcs   += collection.get_amount_of_unique_noncritical_funcs()
            tot_unique_uncategorized_funcs += collection.get_amount_of_unique_uncategorized_funcs()

            for func in collection.get_list():
                func_json = func.__repr__()
                all_funcs.update(func_json)

            # Modified
            collection = log.get_mod_func_collection()

            tot_unique_critical_funcs      += collection.get_amount_of_unique_critical_funcs()
            tot_unique_noncritical_funcs   += collection.get_amount_of_unique_noncritical_funcs()
            tot_unique_uncategorized_funcs += collection.get_amount_of_unique_uncategorized_funcs()

            for func in collection.get_list():
                func_json = func.__repr__()
                all_funcs.update(func_json)

        except Exception as e:
            print(f"{CLI_RED}ERROR DURING FUNC DATA PARSING{CLI_NC}\n - {str(e)}")
            log.set_e(
                f"ERROR DURING FUNC DATA PARSING\n - {''.join(str(e))}"
            )

    with open(f"result/{VERSION_ID}/{PIPELINE_JSON_PATH}", "w") as json_file:
        json.dump(all_funcs, json_file, indent=4, cls=CustomEncoder)
    json_file.close()

    # TODO: Move write_piecharts() into report_generation.py
    write_piecharts(tot_unique_critical_funcs, tot_unique_noncritical_funcs, tot_unique_uncategorized_funcs)
    generate_html_report()

    print(PYTHON_LINE_BREAK)
    print(f"{CLI_GREEN}\nPIPELINE FINISHED.\n{CLI_NC}")
    print(
        f"{CLI_GREEN}\nHTML REPORT HAS BEEN WRITTEN TO{CLI_NC} {PIPELINE_MAIN_HTML_REPORT} ({VERSION_ID})\nExecuted at {datetime.now()}\n"
    )

    for log in logs:
        if log.e:
            print(f"{log.dex_file}: {CLI_RED}{str(log.e)}{CLI_NC}")

    print(PYTHON_LINE_BREAK)


if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"--- {int(minutes)}m {seconds:.2f}s ---")

