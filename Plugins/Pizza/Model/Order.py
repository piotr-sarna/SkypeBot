from typing import TYPE_CHECKING

from Core.TinyDb.ModelBase import ModelBase

if TYPE_CHECKING:
    from Plugins.Pizza.Model.ForcedOrder import ForcedOrder


class Order(ModelBase):
    def with_forced_order(self, forced_order: 'ForcedOrder'):
        self.chat_id = forced_order.chat_id
        self.user_id = forced_order.user_id
        self.user_name = forced_order.user_name
        return self
