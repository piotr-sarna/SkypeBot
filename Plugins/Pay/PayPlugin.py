from Core.PluginBase import PluginBase
from Command import Command


class PayPlugin(PluginBase):
    def keywords(self):
        return ['pay']

    def handle(self, message):
        command = Command.parse(message=message.markup)
        message.chat.sendMsg("Simple response")
        pass

    def help_message(self):
        # TODO
        return "TODO: Fill help message"
