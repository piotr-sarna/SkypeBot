from abc import ABCMeta, abstractmethod


class PluginBase:
    __metaclass__ = ABCMeta

    def __init__(self, skype):
        self._skype = skype

    @abstractmethod
    def friendly_name(self): raise NotImplementedError

    @abstractmethod
    def version(self): raise NotImplementedError

    @abstractmethod
    def keywords(self): raise NotImplementedError

    @abstractmethod
    def handle(self, message): raise NotImplementedError

    @abstractmethod
    def help_message(self): raise NotImplementedError
