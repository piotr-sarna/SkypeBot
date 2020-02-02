from typing import TYPE_CHECKING

from Core.TinyDb.ModelBase import ModelBase

if TYPE_CHECKING:
    from Plugins.Pizza.Model.Order import Order


class ForcedOrder(ModelBase):
    def with_order(self, order: 'Order'):
        self.chat_id = order.chat_id
        self.user_id = order.user_id
        self.user_name = order.user_name
        return self
