import logging
import random
from typing import List

from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.Order import Order
from Plugins.Pizza.Utils.OrdersHelper import OrdersHelper
from Plugins.Pizza.Utils.PizzaCalculator import PizzaCalculator

logger = logging.getLogger(__name__)


class StopHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg):
        super(StopHandler, self).__init__(plugin=plugin, message=message)
        self.__organizer = None

        self.__pizza_calculator = None

    def handle(self):
        logger.debug("Handling for chat '%s'..." % self._chat.id)

        self.__ensure_started()
        self.__ensure_used_by_organizer()

        self.__pizza_calculator = PizzaCalculator(
            orders=self._orders.find_all(chat=self._chat),
            optional_orders=self._optional_orders.find_all(chat=self._chat),
            forced_orders=self._forced_orders.find_all(chat=self._chat)
        )

        self.__pizza_calculator.calculate()

        self.__prepare_messages_components()

        self.__send_user_status()
        self.__send_chat_status()

        self.__remove_organizer()

        self.__send_info_to_removed_users()

    def __ensure_started(self):
        self.__organizer = self._organizers.find_single(chat=self._chat)

        if not self.__organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza started. OK.")

    def __ensure_used_by_organizer(self):
        if self.__organizer.user_id != self._user.id:
            raise Exception(Messages.error_only_owner_can_stop())

        logger.debug("Pizza used by organizer. OK.")

    def __prepare_messages_components(self):
        users_orders = self.__pizza_calculator.users_orders
        self.__orders_summaries = [Messages.order(orders[0], len(orders)) for _, orders in users_orders.items()]

    def __send_user_status(self):
        self._client.send_direct_response(
            Messages.stop_direct(self._message.time,
                                 self.__pizza_calculator.pizzas_to_order,
                                 self.__orders_summaries,
                                 self.__pizza_calculator.lucky_order)
        )

    def __send_chat_status(self):
        self._client.send_group_response(
            Messages.stop_group(self.__organizer,
                                self.__pizza_calculator.pizzas_to_order,
                                self.__orders_summaries,
                                self.__pizza_calculator.lucky_order)
        )

    def __send_info_to_removed_users(self):
        removed_orders = self.__pizza_calculator.users_removed_orders

        if not removed_orders:
            return

        users_orders = self.__pizza_calculator.users_orders

        for user_id, _ in removed_orders.items():
            if user_id in users_orders:
                self._client.send_direct_message(user_id, Messages.order_reduced(len(users_orders[user_id])))
            else:
                self._client.send_direct_message(user_id, Messages.order_removed())

    def __remove_organizer(self):
        self._organizers.remove(model=self.__organizer)
