import re

from src.misc.static import *

class DiffData:

    def __init__(self, old_sig, new_sig, original_diff_code, diff_changes):

        self.old_sig = old_sig
        self.new_sig = new_sig
        self.original_diff_code = original_diff_code
        self.diff_changes = diff_changes

        # Init later used vars
        self.diff_strings = None
        self.source_class = None
        self.source_file = None
        self.source_super = None
        self.source_return_type = None
        self.source_param_types = None
        self.processed_diff_code = None
        self.cf_change = None
        self.diff_ifs = None
        self.number_of_added_else = 0
        self.number_of_deleted_else = 0

        # Process modified diff data
        self.diff_strings = self.extract_strings_from_diff(original_diff_code)

        (
            self.source_class,
            self.source_file,
            self.source_super,
            self.source_return_type,
            self.source_param_types,
        ) = self.extract_diff_metadata(original_diff_code)

        # Strips analysis data from diff code
        self.diff_code_body = self.extract_code(original_diff_code)

        (
            self.cf_change,
            self.diff_ifs,
            self.number_of_added_else,
            self.number_of_deleted_else,
        ) = self.extract_control_flow_change(self.diff_code_body)

    def extract_strings_from_diff(self, diff_body: str) -> list[str]:
        """
        Extracts all quoted strings from the diff body.
        """
        # Regex to capture strings inside double quotes
        string_pattern = re.compile(r'"(.*?)"')

        strings = string_pattern.findall(diff_body)
        return strings

    def extract_diff_metadata(self, diff_body: str):
        """
        Extracts metadata from the diff body including class path, source file, superclass, and method signature.
        """
        # Patterns to extract the required fields
        class_pattern = re.compile(r"Class:\s*(\S+)")
        source_file_pattern = re.compile(r"Source File:\s*(\S+)")
        superclass_pattern = re.compile(r"Superclass:\s*(\S+)")

        # TODO: Doesnt work atm
        method_signature_pattern = re.compile(r"Method Signature:\s*(\S+)\((.*?)\)")

        # Apply regex to extract values
        class_match = class_pattern.search(diff_body)
        source_file_match = source_file_pattern.search(diff_body)
        superclass_match = superclass_pattern.search(diff_body)
        method_signature_match = method_signature_pattern.search(diff_body)

        # Populate metadata dictionary
        self.source_class = class_match.group(1) if class_match else None
        self.source_file = source_file_match.group(1) if source_file_match else None
        self.source_super = superclass_match.group(1) if superclass_match else None
        self.source_return_type = (
            method_signature_match.group(1) if method_signature_match else None
        )
        self.source_param_types = (
            method_signature_match.group(2).strip() if method_signature_match else None
        )

        return (
            self.source_class,
            self.source_file,
            self.source_super,
            self.source_return_type,
            self.source_param_types,
        )
            
    def extract_code(self, original_diff_code: str) -> str:
        """
        Convert a unified diff hunk into “plain code”, while
        keeping the +/- patch markers and discarding /* … */ comments.
        """

        header_re   = re.compile(r'^(?:---|\+\+\+|@@).*?$', re.MULTILINE)

        # keep an optional + or – that may sit right in front of the comment
        comment_re  = re.compile(r'([+-]?)\s*/\*.*?\*/',    re.DOTALL)

        # lines that became empty after the cleanup (just +, – or whitespace)
        blank_re    = re.compile(r'(?m)^[+-]?\s*$')

        txt = header_re.sub('', original_diff_code)          # 1. remove diff headers

        # 2. delete every /* … */ block but re‑insert any leading +/- sign
        txt = comment_re.sub(r'\1', txt)

        # 3. drop completely blank lines that may remain
        txt = blank_re.sub('', txt)

        # 4. squeeze multiple blank lines down to at most one
        txt = re.sub(r'\n{3,}', '\n\n', txt)

        return txt.strip()

    def extract_control_flow_change(self, diff_body: str):
        """
        Extracts all if-statements from the diff body.
        """
        # checks for added or removed 'if' and 'else if'
        ifs = re.findall(r"[+-]\s.*if\s*\(.*\)", diff_body)

        res = [line.replace("+", f"{GREEN}+{NC}") for line in ifs]
        res = [line.replace("-", f"{RED}-{NC}") for line in res]

        # checks for 'else'
        added_else = re.findall(r"\+.*\belse\s*", diff_body)
        deleted_else = re.findall(r"\-.*\belse\s*", diff_body)

        # the actual 'else' statements are not of interest (no condition)
        number_of_added_else = len(added_else)
        number_of_deleted_else = len(deleted_else)

        cf_change = (len(res) + len(added_else) + len(deleted_else)) > 0
        return (cf_change, res, number_of_added_else, number_of_deleted_else)