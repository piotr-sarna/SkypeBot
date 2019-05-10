from Core.PluginBase import PluginBase


class PayPlugin(PluginBase):
    def keywords(self):
        return ['pay']

    def handle(self, message):
        message.chat.sendMsg("Simple response")
        pass
