from Core.PluginBase import PluginBase
from Command import Command


class PayPlugin(PluginBase):
    def keywords(self):
        return ['pay']

    def handle(self, message):
        command = Command.parse(message=message.markup)

        for contact, order_cost in command.order_costs.iteritems():
            message = self._prepare_message(command=command, order_cost=order_cost)

            self._skype.contacts[contact].chat.sendMsg(message)

    def help_message(self):
        # TODO
        return "TODO: Fill help message"

    @staticmethod
    def _prepare_message(command, order_cost):
        divided_delivery_cost = command.delivery_cost / len(command.order_costs)
        final_order_cost = order_cost + divided_delivery_cost
        final_order_cost = float(final_order_cost) / 100

        return "Blik: {}\nNumer konta: {}\nKwota: {}".format(command.blik, command.account_number, final_order_cost)
