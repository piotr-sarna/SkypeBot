import logging

from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Utils.PizzaCalculator import PizzaCalculator

logger = logging.getLogger(__name__)


class StatusHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg):
        super(StatusHandler, self).__init__(plugin=plugin, message=message)
        self.__organizer = None
        self.__pizza_calculator = None

    def handle(self):
        logger.debug("Handling for user '%s' at chat '%s'..." % (self._user.id, self._chat.id))

        self.__ensure_started()

        self.__pizza_calculator = PizzaCalculator(
            orders=self._orders.find_all(chat=self._chat),
            optional_orders=self._optional_orders.find_all(chat=self._chat),
            forced_orders=self._forced_orders.find_all(chat=self._chat)
        )

        self.__pizza_calculator.calculate()

        users_summaries = self.__pizza_calculator.summarize_users_orders()
        users_summaries_msgs = [Messages.status_user_summary(summary=summary) for summary in users_summaries]
        status_message = Messages.status(
            organizer=self.__organizer,
            pizzas=self.__pizza_calculator.pizzas_to_order,
            missing_slices=self.__pizza_calculator.missing_slices_to_next_pizza,
            summaries=users_summaries_msgs
        )

        self._client.send_group_response(status_message)

    def __ensure_started(self):
        self.__organizer = self._organizers.find_single(chat=self._chat)

        if not self.__organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza started. OK.")
