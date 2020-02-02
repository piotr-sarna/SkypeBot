from typing import List

from skpy import SkypeChat, SkypeUser

from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.Order import Order


class OrderRepository(Repository):
    MODEL_CLASS = Order

    def find_all_user(self, user: SkypeUser, chat: SkypeChat) -> List[Order]:
        return super(OrderRepository, self).find_all_user(user=user, chat=chat)
