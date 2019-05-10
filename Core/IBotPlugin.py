from abc import ABCMeta, abstractmethod


class IBotPlugin:
    __metaclass__ = ABCMeta

    @abstractmethod
    def keywords(self): raise NotImplementedError

    @abstractmethod
    def handle(self, message): raise NotImplementedError
