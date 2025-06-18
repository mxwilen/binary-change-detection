from collections import defaultdict
from src.misc.FuncStatus import FuncStatus

class FuncCollection:
    def __init__(self, func_status: FuncStatus):
        self.func_status = func_status
        self.func_collection = []
        self.func_categories = defaultdict(list)
        self.func_keywords = defaultdict(list)
        self.func_collection_metadata = FuncCollectionMetaData()

    def append_func(self, func):
        self.func_collection.append(func)

    def get_categories_from_func(self, func_id):
        keyword = self.func_categories.get(func_id)
        return keyword

    def get_keywords_from_func(self, func_id):
        keyword = self.func_keywords.get(func_id)
        return keyword

    def get_list(self):
        return self.func_collection

    def get_amount_of_funcs(self):
        return len(self.func_collection)
    

    # Getters for amounts
    def get_amount_of_unique_uncategorized_funcs(self):
        return self.func_collection_metadata.amount_of_unique_uncategorized_funcs
    
    def get_amount_of_unique_critical_funcs(self):
        return self.func_collection_metadata.amount_of_unique_critical_funcs

    def get_amount_of_unique_noncritical_funcs(self):
        return self.func_collection_metadata.amount_of_unique_noncritical_funcs

    # Other categorization registrations
    def register_lib_func(self):
        self.func_collection_metadata.register_lib_func()

    def register_unique_uncategorized_func(self):
        self.func_collection_metadata.register_unique_uncategorized_func()

    def register_unique_critical_func(self):
        self.func_collection_metadata.register_unique_critical_func()

    def register_unique_noncritical_func(self):
        self.func_collection_metadata.register_unique_noncritical_func()

    # Critical Categorization registration
    def register_db_change(self):
        self.func_collection_metadata.register_db_change()

    def register_file_change(self):
        self.func_collection_metadata.register_file_write_change()

    def register_logging_change(self):
        self.func_collection_metadata.register_logging_change()

    def register_auth_change(self):
        self.func_collection_metadata.register_auth_change()

    def register_error_change(self):
        self.func_collection_metadata.register_error_change()

    def register_crypto_change(self):
        self.func_collection_metadata.register_crypto_change()

    # Non-critical category registration
    def register_network_change(self):
        self.func_collection_metadata.register_network_change()

    def register_ui_change(self):
        self.func_collection_metadata.register_ui_change()

    def register_text_manipulation_change(self):
        self.func_collection_metadata.register_text_manipulation_change()


class FuncCollectionMetaData:
    def __init__(self):

        # Other categorizations
        self.amount_of_lib_funcs = 0
        self.amount_of_unique_uncategorized_funcs = 0
        self.amount_of_unique_critical_funcs = 0
        self.amount_of_unique_noncritical_funcs = 0

        # Critical
        self.amount_of_db_changes = 0
        self.amount_of_file_writes = 0
        self.amount_of_logging_changes = 0
        self.amount_of_auth_changes = 0
        self.amount_of_error_handlings = 0
        self.amount_of_crypto_handlings = 0

        # Noncritical
        self.amount_of_network_calls = 0
        self.amount_of_ui_updates = 0
        self.amount_of_text_manipulations = 0

    # Other categorization handlers
    def register_lib_func(self):
        self.amount_of_lib_funcs += 1

    def register_unique_uncategorized_func(self):
        self.amount_of_unique_uncategorized_funcs += 1

    def register_unique_critical_func(self):
        self.amount_of_unique_critical_funcs += 1

    def register_unique_noncritical_func(self):
        self.amount_of_unique_noncritical_funcs += 1

    # Critical category handlers
    def register_db_change(self):
        self.amount_of_db_changes += 1

    def register_file_write_change(self):
        self.amount_of_file_writes += 1

    def register_logging_change(self):
        self.amount_of_logging_changes += 1

    def register_auth_change(self):
        self.amount_of_auth_changes += 1

    def register_error_change(self):
        self.amount_of_error_handlings += 1

    def register_crypto_change(self):
        self.amount_of_crypto_handlings += 1

    # Non-critical category handlers
    def register_network_change(self):
        self.amount_of_network_calls += 1

    def register_ui_change(self):
        self.amount_of_ui_updates += 1

    def register_text_manipulation_change(self):
        self.amount_of_text_manipulations += 1
