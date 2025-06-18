from enum import Enum


class Categories(Enum):
    # Classification categories
    C_LIB_FUNC     = "LIBRARY FUNCTION"
    C_DATA_STORAGE = "DATA STORAGE"
    C_FILE_WRITE   = "FILE WRITE"
    C_LOGGING      = "LOGGING CHANGE"
    C_NET_CALL     = "NETWORK CALL"
    C_UI           = "UI UPDATE"
    C_AUTH         = "AUTH CHANGE"
    C_ERROR        = "ERROR HANDLING"
    C_TEXT_MAN     = "TEXT MANIPULATION"
    C_CRYPTO       = "CRYPTOGRAPHIC OPERATION"
    UNCATEGORIZED  = "UNCATEGORIZED"


from src.misc.static import RED, NC, ORANGE, GREEN

class ClassificationType(Enum):
    FLAG_CRITICAL      = f"{RED}[CRITICAL]{NC}"
    FLAG_GENERAL       = f"{ORANGE}[GENERAL]{NC}"
    FLAG_UNCATEGORIZED = f"{GREEN}[UNCATEGORIZED]{NC}"