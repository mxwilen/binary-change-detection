from src.misc.FuncStatus import FuncStatus
from src.misc.FuncCollection import FuncCollection


class GhidriffLog:
    def __init__(self, dex_file):
        self.dex_file = dex_file
        self.e = []
        self.success = True

        # TODO: testa sätt till None
        self.add_func_collection = FuncCollection(FuncStatus.UNKNOWN)
        self.del_func_collection = FuncCollection(FuncStatus.UNKNOWN)
        self.mod_func_collection = FuncCollection(FuncStatus.UNKNOWN)
        self.symbols = []

        self.func_map = {}

    def set_e(self, e):
        self.success = False
        self.e.append(f"{e}\n")

    def set_add_funcs(self, add_func_collection):
        self.add_func_collection = add_func_collection

        for func in add_func_collection.get_list():
            self.func_map[func.id] = func

    def set_del_funcs(self, del_func_collection):
        self.del_func_collection = del_func_collection

        for func in del_func_collection.get_list():
            self.func_map[func.id] = func

    def set_mod_funcs(self, mod_func_collection):
        self.mod_func_collection = mod_func_collection

        for func in mod_func_collection.get_list():
            self.func_map[func.id] = func

    def set_symbols(self, symbols):
        self.symbols = symbols

    def get_add_func_collection(self):
        return self.add_func_collection

    def get_del_func_collection(self):
        return self.del_func_collection

    def get_mod_func_collection(self):
        return self.mod_func_collection

    def replace_old_added_func(self, func):
        self.func_map.update({func.id: func})

    def get_func_from_id(self, func_id):
        return self.func_map.get(func_id)
