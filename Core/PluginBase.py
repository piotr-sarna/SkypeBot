import urllib.parse
from abc import ABCMeta, abstractmethod

from tinydb import TinyDB

from Core.SkypeClient import SkypeClient


class PluginBase:
    __metaclass__ = ABCMeta

    def __init__(self, client: SkypeClient, database: TinyDB):
        self._client = client
        self.__database = database
        self._data_table = database.table(self.__table_name())

    def __table_name(self):
        table_name = "{friendly_name}-{version}".format(friendly_name=self.friendly_name(), version=self.version())
        return urllib.parse.quote(table_name)

    @abstractmethod
    def friendly_name(self): raise NotImplementedError

    @abstractmethod
    def version(self): raise NotImplementedError

    @abstractmethod
    def keywords(self): raise NotImplementedError

    @abstractmethod
    def handle(self, event): raise NotImplementedError

    @abstractmethod
    def help_message(self): raise NotImplementedError
