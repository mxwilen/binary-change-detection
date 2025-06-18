import shortuuid

from src.misc.static import *

from src.misc.FuncStatus import FuncStatus
from src.categorization.static import ClassificationType

class FuncNode:
    """
    * Contains metadata for one unique function/method that has been detected. 
    * The code changes and more specific func details can be found in a funcnodes own DiffData object.
    """

    def __init__(
        self,
        class_name,
        fullname,
        name,
        dex_file,
        parent_func,
        child_func,
        func_status,
        html_diff,
        mod_func_data,
        sig=None,
    ):

        # Meta data
        self.id = shortuuid.uuid()
        self.class_name = class_name
        self.fullname = fullname
        self.name = name
        self.dex_file = dex_file
        self.parent_func = parent_func
        self.child_func = child_func
        self.func_status = func_status
        self.html_diff = html_diff
        self.sig = sig
        self.mod_func_data = mod_func_data

        # TODO: Remove or improve...
        self.is_synthetic = False  # Flag to mark synthetic/lambda functions
        self.is_kotlin_synthetic = (
            False  # Flag to mark kotlin specific synthetic/lambda functions
        )

        # Categorization data
        self.matched_keywords = []
        self.critical_code = []
        self.classification_type = ClassificationType.FLAG_UNCATEGORIZED
        self.classifications = []
        self.critical_classifications = []

        self.cf_change = self.mod_func_data.cf_change
        self.diff_ifs = self.mod_func_data.diff_ifs
        self.number_of_added_else = self.mod_func_data.number_of_added_else
        self.number_of_deleted_else = self.mod_func_data.number_of_deleted_else
        self.sig = self.mod_func_data.new_sig

        self.source_class = self.mod_func_data.source_class
        self.source_file = self.mod_func_data.source_file
        self.source_super = self.mod_func_data.source_super
        self.source_return_type = self.mod_func_data.source_return_type
        self.source_param_types = self.mod_func_data.source_param_types

        self.diff_strings = self.mod_func_data.diff_strings
        self.diff_body = self.mod_func_data.diff_code_body          # Only used as categorization data
        self.diff_changes = self.mod_func_data.diff_changes

        # Evaluation data
        self.eval_rating = 0

    def get_func_id(self):
        return self.id

    def set_synthetic(self):
        self.is_synthetic = True

    def set_kotlin_synthetic(self):
        self.is_kotlin_synthetic = True

    def set_critical(self):
        self.classification_type = ClassificationType.FLAG_CRITICAL

    def set_general(self):
        self.classification_type = ClassificationType.FLAG_GENERAL

    def set_uncategorized(self):
        self.classification_type = ClassificationType.FLAG_UNCATEGORIZED

    def set_critical_code(self, snippet):
        self.critical_code.append(snippet)

    def add_classification(self, classification):
        if classification not in self.classifications:
            self.classifications.append(classification)
            self.set_general()

    def add_critical_classification(self, classification):
        if classification not in self.critical_classifications:
            self.critical_classifications.append(classification)
            self.set_critical()

    def add_matched_keywords(self, list_of_matched_words):
        for word in list_of_matched_words:
            if word.lower() not in self.matched_keywords:
                self.matched_keywords.append(word.lower())

    def get_matched_keywords(self):
        return self.matched_keywords

    def get_classifications(self):
        return self.classifications

    def is_library_function(self, check_source_class=False):
        """
        Checks if the function is part of a library package.
        """

        # List of library prefixes to ignore
        LIBRARY_PREFIXES = [
            "androidx",
            "android",
            "kotlin",
            "java",
            "javax",
            "org.jetbrains",
            "com.google",
            "Ljava",
            "Landroid",
            "Lcom",
            "Lkotlin",
            "okhttp3",
            "okio"
        ]

        name = self.fullname
        if check_source_class:
            if self.source_class:
                name = self.source_class

        for prefix in LIBRARY_PREFIXES:
            if name.startswith(prefix):
                return True
        return False

    def __repr__(self):
        synthetic_flag = f"{YELLOW}[SYNTHETIC]{NC}" if self.is_synthetic else ""
        strings_flag = f"{PINK}[STRINGS FOUND]{NC}" if self.diff_strings else ""
        control_flow_flag = f"{BLUE}[CF CHANGE]{NC}" if self.cf_change else ""
        library_flag = f"{BROWN}[LIBRARY FUNC]{NC}" if self.is_library_function() else ""

        formated_parents = (
            "[" + "".join(f"\n  {p.strip()}" for p in self.parent_func) + "\n]"
        )
        formated_children = (
            "[" + "".join(f"\n  {c.strip()}" for c in self.child_func) + "\n]"
        )
        formated_crit_code = (
            "[" + "".join(f"\n  {code.strip()}" for code in self.critical_code) + "\n]"
        )
        formated_strings = (
            "[" + "".join(f"\n  '{s.strip()}'" for s in self.diff_strings) + "\n]"
        )

        if self.func_status == FuncStatus.MODIFIED:
            formated_ifs = (
                "[" + "".join(f"\n  {c.strip()}" for c in self.diff_ifs) + "\n]"
            )

            # Find the longest key for alignment
            max_key_length = (
                max(len(str(k).strip()) for k in self.diff_changes.keys()) + 1
            )
            formatted_diff_changes = (
                "["
                + "".join(
                    f"\n  {str(k).strip().ljust(max_key_length)}: {str(v).strip()}"
                    for k, v in self.diff_changes.items()
                )
                + "\n]"
            )
        else:
            formated_ifs = formatted_diff_changes = ""

        json_output = {
            str(self.id): {
                # Default table data
                "func_name": f"<pre>{self.name}\n<small>({self.class_name.replace(' (GhidraClass)', '')})</small></pre>",
                "func_status": self.func_status.name,
                "func_eval": self.eval_rating,
                "flag_classification_type": self.classification_type.value,
                "flag_is_synthetic": synthetic_flag,
                "flag_library_func": library_flag,
                "flag_strings_in_diff": strings_flag,
                "flag_control_flow_in_diff": control_flow_flag,

                # Detailed data
                "classname": self.class_name,
                "fullname": self.fullname,
                "signature": self.sig,
                "classifications_critical": self.critical_classifications,
                "classifications_general": self.classifications,
                "classifications_matched_keywords": str(self.matched_keywords),
                "critical_code_changes": formated_crit_code,
                "source_file": self.source_file,
                "source_class": self.source_class,
                "source_superclass": self.source_super,
                "inheritance_parents": formated_parents,
                "inheritance_children": formated_children,
                "code_diff_changes": formatted_diff_changes,
                "code_critical_code_changes": formated_crit_code,
                "code_strings": formated_strings,
                "control_flow_changes_changed_ifs": formated_ifs,
                "control_flow_changes_added_else": self.number_of_added_else,
                "control_flow_changes_deleted_else": self.number_of_deleted_else,
                "html_diff": self.html_diff,
            },
        }

        return json_output
