import urllib.parse
from abc import ABC

from tinydb import TinyDB


class Repository(ABC):
    def __init__(self, database: TinyDB, table_prefix: str):
        self._database = database
        self._table = database.table(urllib.parse.quote("%s_%s" % (table_prefix, type(self).__name__)))
