from Plugins.Pizza.Handlers.HandlerBase import HandlerBase


class HelpHandler(HandlerBase):
    def handle(self):
        self._client.send_direct_response(self._plugin.help_message())
