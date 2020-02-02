import logging

from Plugins.Pizza.Handlers.HandlerBase import HandlerBase

logger = logging.getLogger(__name__)


class HelpHandler(HandlerBase):
    def handle(self):
        logger.debug("Handling for chat '%s'..." % self._chat.id)
        self._client.send_direct_response(self._plugin.help_message())
