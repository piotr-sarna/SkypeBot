import logging
from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.ForcedOrder import ForcedOrder
from Plugins.Pizza.Model.Order import Order
from Plugins.Pizza.Utils.PizzaCalculator import PizzaCalculator

logger = logging.getLogger(__name__)


class SlicesHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg, slices: int):
        super(SlicesHandler, self).__init__(plugin=plugin, message=message)
        self._slices = slices
        self.__orders = None
        self.__forced_orders = None

    def handle(self):
        logger.debug("Handling for user '%s' at chat '%s'..." % (self._user.id, self._chat.id))

        self.__ensure_started()
        self.__refresh_user_orders_cache()

        if len(self.__orders) < self._slices:
            self.__add_slices()
        elif len(self.__orders) > self._slices:
            self.__move_normal_to_forced()
        else:
            logger.debug("Nothing to do")

        self.__trim_forced_orders()
        self.__refresh_user_orders_cache()

        logger.debug("Normal orders: %d, forced orders: %d" % (len(self.__orders), len(self.__forced_orders)))

        self.__send_user_status()
        self.__send_chat_status()

    def __refresh_user_orders_cache(self):
        self.__orders = self._orders.find_all_user(user=self._user, chat=self._chat)
        self.__forced_orders = self._forced_orders.find_all_user(user=self._user, chat=self._chat)

    def __ensure_started(self):
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza started. OK.")

    def __add_slices(self):
        if len(self.__forced_orders) > 0:
            self.__move_forced_to_normal()
            self.__refresh_user_orders_cache()

        orders_to_create = int(self._slices - len(self.__orders))

        if orders_to_create == 0:
            logger.debug("No new orders to create")
            return

        logger.debug("Creating %d new orders" % orders_to_create)

        orders = [Order().with_context(user=self._user, chat=self._chat) for _ in range(orders_to_create)]
        self._orders.insert_multiple(orders)

    def __move_normal_to_forced(self):
        orders_to_remove = self.__orders[self._slices:]
        forced_orders_to_create = [ForcedOrder().with_order(order=order) for order in orders_to_remove]

        logger.debug("Moving %d normal orders to forced" % len(orders_to_remove))

        self._orders.remove_multiple(orders_to_remove)
        self._forced_orders.insert_multiple(forced_orders_to_create)

    def __move_forced_to_normal(self):
        to_move_to_normal = min(len(self.__forced_orders), (self._slices - len(self.__orders)))
        forced_orders_to_remove = self.__forced_orders[:to_move_to_normal]
        orders_to_create = [order.to_order() for order in forced_orders_to_remove]

        logger.debug("Moving %d forced orders to normal" % len(forced_orders_to_remove))

        self._forced_orders.remove_multiple(forced_orders_to_remove)
        self._orders.insert_multiple(orders_to_create)

    def __trim_forced_orders(self):
        orders = self._orders.find_all(chat=self._chat)
        forced_orders = self._forced_orders.find_all(chat=self._chat)
        new_pizza_orders = len(orders) % PizzaCalculator.SLICES_IN_PIZZA
        missing_orders = PizzaCalculator.SLICES_IN_PIZZA - new_pizza_orders

        if new_pizza_orders == 0:
            self._forced_orders.remove_multiple(forced_orders)
        elif missing_orders < len(forced_orders):
            self._forced_orders.remove_multiple(forced_orders[:-missing_orders])

    def __send_user_status(self):
        forced_slices = len(self.__forced_orders)
        self._client.send_direct_response(
            Messages.slices_user_status(slices=self._slices, forced_slices=forced_slices)
        )

    def __send_chat_status(self):
        pizza_calculator = PizzaCalculator(
            orders=self._orders.find_all(chat=self._chat),
            optional_orders=self._optional_orders.find_all(chat=self._chat),
            forced_orders=self._forced_orders.find_all(chat=self._chat)
        )

        pizza_calculator.calculate()

        self._client.send_group_response(Messages.slices_group(
            pizzas=pizza_calculator.pizzas_to_order,
            missing_slices=pizza_calculator.missing_slices_to_next_pizza
        ))
