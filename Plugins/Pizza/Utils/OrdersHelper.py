from collections import defaultdict
from typing import List, Dict, Generator

import itertools

from Plugins.Pizza.Model.Order import Order


class OrdersHelper:
    @staticmethod
    def sort_orders_alternately(orders: List[Order]) -> List[Order]:
        grouped_orders = OrdersHelper.group_by_user_id(orders=orders)
        orders_lists = OrdersHelper.sort_groups_by_doc_id(grouped_orders=grouped_orders)
        return list(OrdersHelper.zip_orders_alternately(orders_lists=orders_lists))

    @staticmethod
    def group_by_user_id(orders: List[Order]) -> Dict[str, List[Order]]:
        grouped_orders = defaultdict(list)

        for order in orders:
            grouped_orders[order.user_id].append(order)

        return grouped_orders

    @staticmethod
    def sort_groups_by_doc_id(grouped_orders: Dict[str, List[Order]]) -> List[List[Order]]:
        orders_lists = [orders for _, orders in grouped_orders.items()]
        return sorted(orders_lists, key=lambda order_list: order_list[0].doc_id)

    @staticmethod
    def zip_orders_alternately(orders_lists: List[List[Order]]) -> Generator[Order, None, None]:
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