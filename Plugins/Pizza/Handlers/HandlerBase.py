from abc import ABC, abstractmethod

from skpy import SkypeMsg, SkypeUser, SkypeChat

from Core.SkypeClient import SkypeClient
from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Repository.ForcedOrderRepository import ForcedOrderRepository
from Plugins.Pizza.Repository.OptionalOrderRepository import OptionalOrderRepository
from Plugins.Pizza.Repository.OrderRepository import OrderRepository
from Plugins.Pizza.Repository.OrganizerRepository import OrganizerRepository


class HandlerBase(ABC):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg):
        self.__plugin = plugin
        self.__message = message

    @property
    def _plugin(self) -> PizzaPlugin:
        return self.__plugin

    @property
    def _message(self) -> SkypeMsg:
        return self.__message

    @property
    def _client(self) -> SkypeClient:
        return self.__plugin.client

    @property
    def _user(self) -> SkypeUser:
        return self.__message.user

    @property
    def _chat(self) -> SkypeChat:
        return self.__message.chat

    @property
    def _organizers(self) -> OrganizerRepository:
        return self.__plugin.repositories.organizer

    @property
    def _orders(self) -> OrderRepository:
        return self.__plugin.repositories.order

    @property
    def _optional_orders(self) -> OptionalOrderRepository:
        return self.__plugin.repositories.optional_order

    @property
    def _forced_orders(self) -> ForcedOrderRepository:
        return self.__plugin.repositories.forced_order

    @abstractmethod
    def handle(self):
        pass
