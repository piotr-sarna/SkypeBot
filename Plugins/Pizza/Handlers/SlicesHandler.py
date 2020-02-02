from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages


class SlicesHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg, slices: int):
        super(SlicesHandler, self).__init__(plugin=plugin, message=message)
        self._slices = slices

    def handle(self):
        TODO_orders = []
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        existing_idx = [idx for idx, order in enumerate(TODO_orders) if order[0].id == self._user.id]

        if existing_idx:
            TODO_orders.pop(existing_idx[0])

        if self._slices > 0:
            TODO_orders.append((self._user, self._slices))

        total_ordered_slices = sum(order[1] for order in TODO_orders)
        missing_slices = self._plugin.SLICES_IN_PIZZA - total_ordered_slices % self._plugin.SLICES_IN_PIZZA
        pizzas_to_order = total_ordered_slices // self._plugin.SLICES_IN_PIZZA

        self._client.send_direct_response(Messages.slices_direct(self._slices))
        self._client.send_group_response(Messages.slices_group(pizzas_to_order, missing_slices))
