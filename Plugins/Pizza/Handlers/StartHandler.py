import logging
from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.Organizer import Organizer

logger = logging.getLogger(__name__)


class StartHandler(HandlerBase):
    def __init__(self, plugin: PizzaPlugin, message: SkypeMsg):
        super(StartHandler, self).__init__(plugin=plugin, message=message)
        self.__organizer = None

    def handle(self):
        logger.debug("Handling for chat '%s'..." % self._chat.id)

        self.__ensure_not_started()
        self.__save_organizer()
        self.__clear_all_orders()

        self.__send_user_status()
        self.__send_chat_status()

    def __ensure_not_started(self):
        self.__organizer = self._organizers.find_single(chat=self._chat)

        if self.__organizer:
            raise Exception(Messages.error_not_started())

        logger.debug("Pizza NOT started. OK.")

    def __save_organizer(self):
        logger.debug("Saving organizer")
        self.__organizer = Organizer().with_context(user=self._user, chat=self._chat)
        self._organizers.insert(model=self.__organizer)

    def __clear_all_orders(self):
        logger.debug("Clearing all orders")
        self._orders.remove_all(chat=self._chat)
        self._optional_orders.remove_all(chat=self._chat)
        self._forced_orders.remove_all(chat=self._chat)

    def __send_user_status(self):
        self._client.send_direct_response(Messages().start_direct(self._message.time))

    def __send_chat_status(self):
        self._client.send_group_response(Messages().start_group(self.__organizer))
