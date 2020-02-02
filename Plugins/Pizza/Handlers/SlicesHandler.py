import logging
from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.ForcedOrder import ForcedOrder
from Plugins.Pizza.Model.Order import Order


logger = logging.getLogger(__name__)


class SlicesHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg, slices: int):
        super(SlicesHandler, self).__init__(plugin=plugin, message=message)
        self._slices = slices
        self.__orders = None
        self.__forced_orders = None

    def handle(self):
        logger.debug("Handling...")

        self.__ensure_started()
        self.__orders = self._orders.find_all_user(user=self._user, chat=self._chat)
        self.__forced_orders = self._forced_orders.find_all_user(user=self._user, chat=self._chat)

        if len(self.__orders) < self._slices:
            self.__add_slices()
        elif len(self.__orders) > self._slices:
            self.__move_normal_to_forced()
        else:
            logger.debug("Nothing to do")

        logger.debug("Normal orders: %d, forced orders: %d" % (len(self.__orders), len(self.__forced_orders)))

        self.__send_user_status()
        self.__send_chat_status()

    def __ensure_started(self):
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza started. OK.")

    def __add_slices(self):
        if len(self.__forced_orders) > 0:
            self.__move_forced_to_normal()

        orders_to_create = int(self._slices - len(self.__orders))

        if orders_to_create == 0:
            logger.debug("No new orders to create")
            return

        logger.debug("Creating %d new orders" % orders_to_create)

        orders = [Order().with_context(user=self._user, chat=self._chat) for _ in range(orders_to_create)]
        self._orders.insert_multiple(orders)
        self.__orders += orders

    def __move_normal_to_forced(self):
        orders_to_remove = self.__orders[self._slices:]
        forced_orders_to_create = [ForcedOrder().with_order(order=order) for order in orders_to_remove]

        logger.debug("Moving %d normal orders to forced" % len(orders_to_remove))

        self._orders.remove_multiple(orders_to_remove)
        self._forced_orders.insert_multiple(forced_orders_to_create)

        self.__orders = [order for order in self.__orders if order not in orders_to_remove]
        self.__forced_orders += forced_orders_to_create

    def __move_forced_to_normal(self):
        to_move_to_normal = min(len(self.__forced_orders), (self._slices - len(self.__orders)))
        forced_orders_to_remove = self.__forced_orders[:to_move_to_normal]
        orders_to_create = [Order().with_forced_order(forced_order=order) for order in forced_orders_to_remove]

        logger.debug("Moving %d forced orders to normal" % len(forced_orders_to_remove))

        self._forced_orders.remove_multiple(forced_orders_to_remove)
        self._orders.insert_multiple(orders_to_create)

        self.__forced_orders = [order for order in self.__forced_orders if order not in forced_orders_to_remove]
        self.__orders += orders_to_create

    def __send_user_status(self):
        forced_slices = len(self.__forced_orders)
        message = Messages.slices_user_status_normal(slices=self._slices) \
            if forced_slices == 0 \
            else Messages.slices_user_status_forced(slices=self._slices, forced_slices=forced_slices)
        self._client.send_direct_response(message)

    def __send_chat_status(self):
        all_slices = len(self._orders.find_all(chat=self._chat))
        missing_slices = self._plugin.SLICES_IN_PIZZA - all_slices % self._plugin.SLICES_IN_PIZZA

        if missing_slices > 0:
            optional_orders = len(self._optional_orders.find_all(chat=self._chat))
            forced_orders = len(self._forced_orders.find_all(chat=self._chat))

            if optional_orders + forced_orders >= missing_slices:
                all_slices += missing_slices
                missing_slices = 0

        pizzas_to_order = all_slices // self._plugin.SLICES_IN_PIZZA

        self._client.send_group_response(Messages.slices_group(pizzas_to_order, missing_slices))
