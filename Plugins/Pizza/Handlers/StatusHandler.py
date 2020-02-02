from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages


class StatusHandler(HandlerBase):
    def handle(self):
        TODO_orders = []
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        final_order = list(TODO_orders)
        overflow_order = list()
        total_ordered_slices = sum(order[1] for order in final_order)
        number_of_pizzas = int(total_ordered_slices / self._plugin.SLICES_IN_PIZZA)
        missing_slices = self._plugin.SLICES_IN_PIZZA - total_ordered_slices % self._plugin.SLICES_IN_PIZZA
        slices_overflow = total_ordered_slices % self._plugin.SLICES_IN_PIZZA

        if slices_overflow:
            for idx, order in reversed(list(enumerate(TODO_orders))):
                if order[1] <= slices_overflow:
                    final_order.pop(idx)
                    slices_overflow -= order[1]
                    overflow_order.append(order)
                else:
                    new_slices = final_order[idx][1] - slices_overflow
                    final_order[idx] = (final_order[idx][0], new_slices)
                    overflow_order.append((final_order[idx][0], slices_overflow))
                    slices_overflow = 0

                if not slices_overflow:
                    break

        overflow_order = reversed(overflow_order)
        orders_summaries = [Messages.order(order[0], order[1]) for order in final_order]
        overflow_summaries = [Messages.order(order[0], order[1]) for order in overflow_order]

        status_message = Messages.status(organizer, number_of_pizzas, missing_slices, orders_summaries, overflow_summaries)
        self._client.send_group_response(status_message)
