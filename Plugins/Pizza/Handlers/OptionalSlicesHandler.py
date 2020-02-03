import logging
from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.OptionalOrder import OptionalOrder
from Plugins.Pizza.Utils.PizzaCalculator import PizzaCalculator

logger = logging.getLogger(__name__)


class OptionalSlicesHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg, slices: int):
        super(OptionalSlicesHandler, self).__init__(plugin=plugin, message=message)
        self._slices = slices
        self.__optional_orders = None

    def handle(self):
        logger.debug("Handling for chat '%s'..." % self._chat.id)

        self.__ensure_started()
        self.__optional_orders = self._optional_orders.find_all_user(user=self._user, chat=self._chat)

        if len(self.__optional_orders) < self._slices:
            self.__add_slices()
        elif len(self.__optional_orders) > self._slices:
            self.__remove_slices()
        else:
            logger.debug("Nothing to do")

        logger.debug("Optional orders: %d" % len(self.__optional_orders))

        self.__send_user_status()
        self.__send_chat_status()

    def __ensure_started(self):
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza started. OK.")

    def __add_slices(self):
        orders_to_create = int(self._slices - len(self.__optional_orders))

        logger.debug("Creating %d new optional orders" % orders_to_create)

        orders = [OptionalOrder().with_context(user=self._user, chat=self._chat) for _ in range(orders_to_create)]
        self._optional_orders.insert_multiple(orders)
        self.__optional_orders += orders

    def __remove_slices(self):
        orders_to_remove = self.__optional_orders[self._slices:]

        logger.debug("Removing %d optional orders" % len(orders_to_remove))

        self._optional_orders.remove_multiple(orders_to_remove)
        self.__optional_orders = [order for order in self.__optional_orders if order not in orders_to_remove]

    def __send_user_status(self):
        self._client.send_direct_response(Messages.optional_slices_user_status(optional_slices=self._slices))

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
