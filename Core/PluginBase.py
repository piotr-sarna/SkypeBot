from abc import ABCMeta, abstractmethod


class PluginBase:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._client = None

    def set_client(self, client):
        self._client = client

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
