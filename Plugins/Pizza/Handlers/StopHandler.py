import logging
import random
from typing import List, Dict, Generator

from collections import defaultdict

import itertools
from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.Order import Order

logger = logging.getLogger(__name__)


class StopHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg):
        super(StopHandler, self).__init__(plugin=plugin, message=message)
        self.__organizer = None

        self.__final_orders = None
        self.__original_orders = None
        self.__lucky_order = None

        self.__missing_orders_count = None
        self.__optional_orders = None

        self.__redundant_orders_count = None
        self.__reduced_orders = None
        self.__removed_orders = None

        self.__pizzas_count = None
        self.__users_orders = None

        self.__orders_summaries = None

    def handle(self):
        logger.debug("Handling for chat '%s'..." % self._chat.id)

        self.__ensure_started()
        self.__ensure_used_by_organizer()

        self.__complete_order()
        self.__roll_lucky_order()

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

    def __complete_order(self):
        self.__original_orders = self._orders.find_all(chat=self._chat)
        self.__try_complete_order()

        if self.__missing_orders_count == 0:
            logger.debug("Order completed")
            self.__final_orders = self.__original_orders + self.__optional_orders
        else:
            self.__reduce_original_orders()
            logger.debug("Order reduced")
            self.__final_orders = self.__reduced_orders

    def __try_complete_order(self):
        logger.debug("Trying to complete order")

        self.__missing_orders_count = self._plugin.SLICES_IN_PIZZA - len(self.__original_orders) % self._plugin.SLICES_IN_PIZZA

        logger.debug("Total %d pizza orders missing" % self.__missing_orders_count)

        if self.__missing_orders_count > 0:
            optional_orders = self._optional_orders.find_all(chat=self._chat)
            self.__try_complete_pizza(orders=optional_orders)
            logger.debug("%d pizza orders missing after applying optional orders" % self.__missing_orders_count)

        if self.__missing_orders_count > 0:
            forced_orders = self._forced_orders.find_all(chat=self._chat)
            self.__try_complete_pizza(orders=forced_orders)
            logger.debug("%d pizza orders missing after applying forced orders" % self.__missing_orders_count)

    def __try_complete_pizza(self, orders: List[Order]):
        logger.debug("Trying to complete order with %d orders", len(orders))

        if len(orders) == 0:
            return

        too_many_orders = len(orders) > self.__missing_orders_count
        orders_to_map = orders if not too_many_orders else self.__sort_orders_alternately(orders=orders)
        self.__missing_orders_count -= min(len(orders_to_map), self.__missing_orders_count)
        self.__optional_orders = [order.to_order() for order in orders_to_map]

    def __sort_orders_alternately(self, orders: List[Order]) -> List[Order]:
        grouped_orders = self.__group_by_user_id(orders=orders)
        orders_lists = self.__sort_groups_by_doc_id(grouped_orders=grouped_orders)
        return list(self.__zip_orders_alternately(orders_lists=orders_lists))

    @staticmethod
    def __group_by_user_id(orders: List[Order]) -> Dict[str, List[Order]]:
        grouped_orders = defaultdict(list)

        for order in orders:
            grouped_orders[order.user_id].append(order)

        return grouped_orders

    @staticmethod
    def __sort_groups_by_doc_id(grouped_orders: Dict[str, List[Order]]) -> List[List[Order]]:
        orders_lists = [orders for _, orders in grouped_orders.items()]
        return sorted(orders_lists, key=lambda order_list: order_list[0].doc_id)

    @staticmethod
    def __zip_orders_alternately(orders_lists: List[List[Order]]) -> Generator[Order, None, None]:
        # Recipe credited to George Sakkis
        pending = len(orders_lists)
        next_orders = itertools.cycle(iter(orders_list).__next__ for orders_list in orders_lists)

        while pending:
            try:
                for next_order in next_orders:
                    yield next_order()
            except StopIteration:
                pending -= 1
                next_orders = itertools.cycle(itertools.islice(next_orders, pending))

    def __reduce_original_orders(self):
        logger.debug("Reducing order")
        self.__redundant_orders_count = len(self.__original_orders) % self._plugin.SLICES_IN_PIZZA
        logger.debug("Total %d pizza orders redundant" % self.__redundant_orders_count)

        self.__reduced_orders = list(self.__original_orders)
        self.__removed_orders = []

        for _ in range(self.__redundant_orders_count):
            self.__removed_orders.append(self.__reduced_orders.pop())

    def __roll_lucky_order(self):
        logger.debug("Rolling lucky order")
        self.__lucky_order = random.choice(self.__final_orders) if self.__final_orders else None

    def __prepare_messages_components(self):
        self.__pizzas_count = len(self.__final_orders) // self._plugin.SLICES_IN_PIZZA
        self.__users_orders = self.__group_by_user_id(orders=self.__final_orders)
        self.__orders_summaries = [Messages.order(orders[0], len(orders)) for _, orders in self.__users_orders.items()]

    def __send_user_status(self):
        self._client.send_direct_response(
            Messages.stop_direct(self._message.time, self.__pizzas_count, self.__orders_summaries, self.__lucky_order)
        )

    def __send_chat_status(self):
        self._client.send_group_response(
            Messages.stop_group(self.__organizer, self.__pizzas_count, self.__orders_summaries, self.__lucky_order)
        )

    def __send_info_to_removed_users(self):
        if not self.__removed_orders:
            return

        for user_id, _ in self.__group_by_user_id(orders=self.__removed_orders).items():
            if user_id in self.__users_orders:
                self._client.send_direct_message(user_id, Messages.order_reduced(len(self.__users_orders[user_id])))
            else:
                self._client.send_direct_message(user_id, Messages.order_removed())

    def __remove_organizer(self):
        self._organizers.remove(model=self.__organizer)
