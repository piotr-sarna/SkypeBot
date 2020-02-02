from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages


class StopHandler(HandlerBase):
    def handle(self):
        TODO_orders = []
        organizer = self._organizers.find_single(chat=self._chat)

        if not organizer:
            raise Exception(Messages.error_not_started())

        if organizer.user_id != self._message.userId:
            raise Exception(Messages.error_only_owner_can_stop())

        final_order = list(TODO_orders)
        total_ordered_slices = sum(order[1] for order in final_order)
        number_of_pizzas = int(total_ordered_slices / self._plugin.SLICES_IN_PIZZA)
        slices_overflow = total_ordered_slices % self._plugin.SLICES_IN_PIZZA

        if slices_overflow:
            for idx, order in reversed(list(enumerate(TODO_orders))):
                if order[1] <= slices_overflow:
                    final_order.pop(idx)
                    slices_overflow -= order[1]
                    self._client.send_direct_message(order[0].id, Messages.order_removed())
                else:
                    new_slices = final_order[idx][1] - slices_overflow
                    final_order[idx] = (final_order[idx][0], new_slices)
                    slices_overflow = 0
                    self._client.send_direct_message(order[0].id, Messages.order_reduced(new_slices))

                if not slices_overflow:
                    break

        orders_summaries = [Messages.order(order[0], order[1]) for order in final_order]

        self._client.send_direct_response(Messages.stop_direct(self._message.time, number_of_pizzas, orders_summaries))
        self._client.send_group_response(Messages.stop_group(organizer, number_of_pizzas, orders_summaries))

        self._organizers.remove(model=organizer)
