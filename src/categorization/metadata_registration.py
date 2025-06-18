from src.misc.FuncNode import FuncNode
from src.misc.FuncCollection import FuncCollection
from src.categorization.static import Categories
from src.categorization.static import ClassificationType


def register_classification_metadata(func: FuncNode, func_collection: FuncCollection):

    for category in func.classifications:
        match category:
            case Categories.C_LIB_FUNC:
                func_collection.register_lib_func()
            case Categories.C_NET_CALL:
                func_collection.register_network_change()
            case Categories.C_UI:
                func_collection.register_ui_change()
            case Categories.C_TEXT_MAN:
                func_collection.register_text_manipulation_change()

            case _:
                return None
            
    for category in func.critical_classifications:
        match category:
            case Categories.C_DATA_STORAGE:
                func_collection.register_db_change()
            case Categories.C_FILE_WRITE:
                func_collection.register_file_change()
            case Categories.C_LOGGING:
                func_collection.register_logging_change()
            case Categories.C_ERROR:
                func_collection.register_error_change()
            case Categories.C_AUTH:
                func_collection.register_auth_change()
            case Categories.C_CRYPTO:
                func_collection.register_crypto_change()

            case _:
                return None
    
    if func.classification_type == ClassificationType.FLAG_CRITICAL:
        func_collection.register_unique_critical_func()
    elif func.classification_type == ClassificationType.FLAG_GENERAL:
        func_collection.register_unique_noncritical_func()
    elif func.classification_type == ClassificationType.FLAG_UNCATEGORIZED:
        func_collection.register_unique_uncategorized_func()
