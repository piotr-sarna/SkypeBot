from abc import ABC, abstractmethod

from tinydb import TinyDB

from Core.SkypeClient import SkypeClient


class PluginBase(ABC):
    def __init__(self, client: SkypeClient, database: TinyDB):
        self._client = client
        _ = database

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
