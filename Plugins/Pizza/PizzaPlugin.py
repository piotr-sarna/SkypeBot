from skpy import SkypeNewMessageEvent, SkypeEditMessageEvent

from Core.PluginBase import PluginBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.Organizer import Organizer
from Plugins.Pizza.TinyDb.OrganizerRepository import OrganizerRepository
from .Command import Command

SLICES_IN_PIZZA = 8


class PizzaPlugin(PluginBase):
    def __init__(self, client, database):
        super(PizzaPlugin, self).__init__(client=client, database=database)
        self._orders = []
        self.__organizer_repository = OrganizerRepository(database=database, table_prefix=self.friendly_name())

    def friendly_name(self):
        return 'Pizza plugin'

    def version(self):
        return '0.2'

    def keywords(self):
        return ['pizza']

    def handle(self, event):
        if not isinstance(event, SkypeNewMessageEvent) and not isinstance(event, SkypeEditMessageEvent):
            return

        message = event.msg
        command = Command.parse(message=message.markup)

        if command.help:
            self._client.send_direct_response(self.help_message())
            return

        if command.start:
            self._handle_start(message=message, command=command)
        elif command.stop:
            self._handle_stop(message=message, command=command)
        elif command.number_of_slices is not None:
            self._handle_number_of_slices(message=message, command=command)
        elif command.status:
            self._handle_status(message=message, command=command)

    def help_message(self):
        return Messages(self).help()

    def _handle_start(self, message, command):
        organizer = self.__organizer_repository.find_single_at_chat(chat=message.chat)

        if organizer:
            raise Exception(Messages(self).error_only_one_pizza())

        organizer = Organizer().in_context(user=message.user, chat=message.chat)
        self.__organizer_repository.insert(organizer=organizer)

        self._orders = []

        self._client.send_direct_response(Messages(self).start_direct(message.time))
        self._client.send_group_response(Messages(self).start_group(organizer))

    def _handle_stop(self, message, command):
        organizer = self.__organizer_repository.find_single_at_chat(chat=message.chat)

        if not organizer:
            raise Exception(Messages(self).error_not_started())

        if organizer.user_id != message.userId:
            raise Exception(Messages(self).error_only_owner_can_stop())

        final_order = list(self._orders)
        total_ordered_slices = sum(order[1] for order in final_order)
        number_of_pizzas = int(total_ordered_slices / SLICES_IN_PIZZA)
        slices_overflow = total_ordered_slices % SLICES_IN_PIZZA

        if slices_overflow:
            for idx, order in reversed(list(enumerate(self._orders))):
                if order[1] <= slices_overflow:
                    final_order.pop(idx)
                    slices_overflow -= order[1]
                    self._client.send_direct_message(order[0].id, Messages(self).order_removed())
                else:
                    new_slices = final_order[idx][1] - slices_overflow
                    final_order[idx] = (final_order[idx][0], new_slices)
                    slices_overflow = 0
                    self._client.send_direct_message(order[0].id, Messages(self).order_reduced(new_slices))

                if not slices_overflow:
                    break

        orders_summaries = [Messages(self).order(order[0], order[1]) for order in final_order]

        self._client.send_direct_response(Messages(self).stop_direct(message.time, number_of_pizzas, orders_summaries))
        self._client.send_group_response(Messages(self).stop_group(organizer, number_of_pizzas, orders_summaries))

        self.__organizer_repository.remove(organizer=organizer)
        self._orders = []

    def _handle_number_of_slices(self, message, command):
        organizer = self.__organizer_repository.find_single_at_chat(chat=message.chat)

        if not organizer:
            raise Exception(Messages(self).error_not_started())

        existing_idx = [idx for idx, order in enumerate(self._orders) if order[0].id == message.userId]

        if existing_idx:
            self._orders.pop(existing_idx[0])

        if command.number_of_slices > 0:
            self._orders.append((message.user, command.number_of_slices))

        total_ordered_slices = sum(order[1] for order in self._orders)
        missing_slices = SLICES_IN_PIZZA - total_ordered_slices % SLICES_IN_PIZZA
        pizzas_to_order = total_ordered_slices // SLICES_IN_PIZZA

        self._client.send_direct_response(Messages(self).slices_direct(command.number_of_slices))
        self._client.send_group_response(Messages(self).slices_group(pizzas_to_order, missing_slices))
        
    def _handle_status(self, message, command):
        organizer = self.__organizer_repository.find_single_at_chat(chat=message.chat)

        if not organizer:
            raise Exception(Messages(self).error_not_started())

        final_order = list(self._orders)
        overflow_order = list()
        total_ordered_slices = sum(order[1] for order in final_order)
        number_of_pizzas = int(total_ordered_slices / SLICES_IN_PIZZA)
        missing_slices = SLICES_IN_PIZZA - total_ordered_slices % SLICES_IN_PIZZA
        slices_overflow = total_ordered_slices % SLICES_IN_PIZZA

        if slices_overflow:
            for idx, order in reversed(list(enumerate(self._orders))):
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
        orders_summaries = [Messages(self).order(order[0], order[1]) for order in final_order]
        overflow_summaries = [Messages(self).order(order[0], order[1]) for order in overflow_order]

        status_message = Messages(self).status(organizer, number_of_pizzas, missing_slices, orders_summaries, overflow_summaries)
        self._client.send_group_response(status_message)
