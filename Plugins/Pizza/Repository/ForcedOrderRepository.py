from typing import List

from skpy import SkypeChat, SkypeUser

from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.ForcedOrder import ForcedOrder


class ForcedOrderRepository(Repository):
    MODEL_CLASS = ForcedOrder

    def find_all_user(self, user: SkypeUser, chat: SkypeChat) -> List[ForcedOrder]:
        return super(ForcedOrderRepository, self).find_all_user(user=user, chat=chat)
