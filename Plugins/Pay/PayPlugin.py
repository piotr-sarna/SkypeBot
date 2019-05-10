import io
import qrcode
from PIL import Image

from Core.PluginBase import PluginBase
from Command import Command


class PayPlugin(PluginBase):
    def keywords(self):
        return ['pay']

    def handle(self, message):
        command = Command.parse(message=message.markup)

        for contact, order_cost in command.order_costs.iteritems():
            final_order_cost = self._calculate_final_order_cost(command=command, order_cost=order_cost)
            message = self._prepare_message(command=command, final_order_cost=final_order_cost)
            qr_code = self._prepare_qrcode(command=command, final_order_cost=final_order_cost)

            self._skype.contacts[contact].chat.sendMsg(message)

            if qr_code:
                self._skype.contacts[contact].chat.sendFile(qr_code, "qr_code.png", image=True)

    def help_message(self):
        # TODO
        return "TODO: Fill help message"

    @staticmethod
    def _prepare_message(command, final_order_cost):
        return "Blik: {}\nNumer konta: {}\nKwota: {}".format(command.blik, command.account_number, float(final_order_cost)/100)

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

        qr_code = qrcode.make(qr_code_text)
        img_byte_arr = io.BytesIO()
        qr_code.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return img_byte_arr

    @staticmethod
    def _calculate_final_order_cost(command, order_cost):
        divided_delivery_cost = command.delivery_cost / len(command.order_costs)
        return order_cost + divided_delivery_cost
