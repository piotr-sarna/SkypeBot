import io
import qrcode

from Core.PluginBase import PluginBase
from Command import Command


class PayPlugin(PluginBase):
    def friendly_name(self):
        return 'Pay plugin'

    def version(self):
        return '0.1'

    def keywords(self):
        return ['pay']

    def handle(self, message):
        command = Command.parse(message=message.markup)

        if command.help:
            self._skype.contacts[message.userId].chat.sendMsg(self.help_message())
            return

        for contact, order_cost in command.order_costs.iteritems():
            final_order_cost = self._calculate_final_order_cost(command=command, order_cost=order_cost)
            message = self._prepare_message(command=command, final_order_cost=final_order_cost)
            qr_code = self._prepare_qrcode(command=command, final_order_cost=final_order_cost)

            self._skype.contacts[contact].chat.sendMsg(message)

            if qr_code:
                self._skype.contacts[contact].chat.sendFile(qr_code, "qr_code.png", image=True)

    def help_message(self):
        return """{friendly_name} v{version}

Keywords: {keywords}
Commands:
    #help - Displays this help message
    #blik - Telephone number for Blik transfer
    #acc_number - Bank account number
    #acc_name - Bank account holder's name
    #title - Transfer title
    #delivery AMOUNT - Delivery total cost, it will be split equally among all participants
    @SKYPEID AMOUNT - Skype ID of the participant and cost
""".format(friendly_name=self.friendly_name(),
           version=self.version(),
           keywords=','.join(['#' + keyword for keyword in self.keywords()])
           )

    @staticmethod
    def _prepare_message(command, final_order_cost):
        return "Blik: {}\nAccount number: {}\nAmount: {}".format(command.blik, command.account_number, float(final_order_cost)/100)

    @staticmethod
    def _prepare_qrcode(command, final_order_cost):
        if command.account_number is None:
            return None

        qr_code_text = "|PL|{}|{}|{}|{}|||".format(
            "".join(command.account_number.split()),
            final_order_cost,
            command.account_owner_name.upper() if command.account_owner_name else "",
            command.transfer_title if command.transfer_title else "",
        )

        qr_code = qrcode.make(qr_code_text, box_size=5, border=12)
        img_byte_arr = io.BytesIO()
        qr_code.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return img_byte_arr

    @staticmethod
    def _calculate_final_order_cost(command, order_cost):
        divided_delivery_cost = command.delivery_cost / len(command.order_costs)
        return order_cost + divided_delivery_cost
