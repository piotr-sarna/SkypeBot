import itertools
import logging
import random
from collections import namedtuple
from typing import List, Dict

from Plugins.Pizza.Model.ForcedOrder import ForcedOrder
from Plugins.Pizza.Model.OptionalOrder import OptionalOrder
from Plugins.Pizza.Model.Order import Order
from Plugins.Pizza.Utils.OrdersHelper import OrdersHelper

logger = logging.getLogger(__name__)

OrderSummary = namedtuple('OrderSummary', ['user_id', 'user_name', 'order', 'registered', 'optional', 'to_remove'])


class PizzaCalculator:
    SLICES_IN_PIZZA = 8

    def __init__(self, orders: List[Order], optional_orders: List[OptionalOrder], forced_orders: List[ForcedOrder]):
        self.__orders = orders
        self.__optional_orders = optional_orders
        self.__forced_orders = forced_orders
        self.__calculated = False

        self.__selected_optional_orders = []

        self.__final_orders = None
        self.__reduced_orders = None
        self.__removed_orders = None
        self.__lucky_order = None

        self.__missing_orders_count = None

    def calculate(self):
        if self.__calculated:
            return

        self.__calculated = True
        self.__try_complete_order()

        if self.__missing_orders_count == 0:
            logger.debug("Order completed")
            self.__final_orders = self.__orders + self.__selected_optional_orders
        else:
            self.__reduce_order()
            logger.debug("Order reduced")
            self.__final_orders = self.__reduced_orders

        logger.debug("Rolling lucky order")
        self.__lucky_order = random.choice(self.__final_orders) if self.__final_orders else None

    @property
    def pizzas_to_order(self) -> int:
        return len(self.__final_orders) // self.SLICES_IN_PIZZA

    @property
    def missing_slices_to_next_pizza(self) -> int:
        orders = len(self.__orders)
        optional_orders = len(self.__optional_orders)
        forced_orders = len(self.__forced_orders)
        missing_slices = self.SLICES_IN_PIZZA - orders % self.SLICES_IN_PIZZA

        return missing_slices - min(missing_slices, optional_orders + forced_orders)

    @property
    def lucky_order(self) -> Order:
        return self.__lucky_order

    @property
    def users_orders(self) -> Dict[str, List[Order]]:
        return OrdersHelper.group_by_user_id(orders=self.__final_orders)

    @property
    def users_removed_orders(self) -> Dict[str, List[Order]]:
        return OrdersHelper.group_by_user_id(orders=self.__removed_orders)

    def summarize_users_orders(self) -> List[OrderSummary]:
        users_orders = self.users_orders
        all_orders = [self.__orders, self.__optional_orders, self.__forced_orders]
        all_orders = list(itertools.chain.from_iterable(all_orders))
        grouped_orders = OrdersHelper.group_by_user_id(orders=all_orders)

        return [OrderSummary(
            user_id=user_id,
            user_name=orders[0].user_name,
            order=len(users_orders[user_id]),
            registered=len([order for order in orders if type(order) == Order]),
            optional=len([order for order in orders if type(order) == OptionalOrder]),
            to_remove=len([order for order in orders if type(order) == ForcedOrder])
        ) for user_id, orders in grouped_orders.items()]

    def __try_complete_order(self):
        logger.debug("Trying to complete order")

        self.__missing_orders_count = self.SLICES_IN_PIZZA - len(self.__orders) % self.SLICES_IN_PIZZA

        logger.debug("Total %d pizza orders missing" % self.__missing_orders_count)

        if self.__missing_orders_count > 0:
            self.__try_complete_pizza(orders=self.__optional_orders)
            logger.debug("%d pizza orders missing after applying optional orders" % self.__missing_orders_count)

        if self.__missing_orders_count > 0:
            self.__try_complete_pizza(orders=self.__forced_orders)
            logger.debug("%d pizza orders missing after applying forced orders" % self.__missing_orders_count)

    def __try_complete_pizza(self, orders: List[Order]):
        logger.debug("Trying to complete order with %d orders", len(orders))

        if len(orders) == 0:
            return

        too_many_orders = len(orders) > self.__missing_orders_count
        orders_to_map = orders if not too_many_orders else OrdersHelper.sort_orders_alternately(orders=orders)
        self.__missing_orders_count -= min(len(orders_to_map), self.__missing_orders_count)
        self.__selected_optional_orders += [order for order in orders_to_map]

    def __reduce_order(self):
        logger.debug("Reducing order")
        redundant_orders_count = len(self.__orders) % self.SLICES_IN_PIZZA
        logger.debug("Total %d pizza orders redundant" % redundant_orders_count)

        self.__reduced_orders = list(self.__orders)
        self.__removed_orders = []

        for _ in range(redundant_orders_count):
            self.__removed_orders.append(self.__reduced_orders.pop())
