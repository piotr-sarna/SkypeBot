import logging
from typing import List

from skpy import SkypeEventLoop, SkypeMessageEvent, SkypeEditMessageEvent, SkypeConnection

from Core.PluginBase import PluginBase

logger = logging.getLogger(__name__)


class SkypeClient(SkypeEventLoop):
    def __init__(self, username: str, password: str, token_file: str, plugins: List[PluginBase]):
        super(SkypeClient, self).__init__(user=username, pwd=password, tokenFile=token_file)

        self.__add_client_to_plugins(plugins=plugins)

        self._handlers = dict(self.__generate_handlers(plugins=plugins))
        self.__current_event = None
        self.__current_handler = None

    def onEvent(self, event):
        is_message_event = isinstance(event, SkypeMessageEvent)
        is_bots_message = is_message_event and event.msg.userId == self.userId

        if is_message_event and not is_bots_message:
            self.__process_message_event(event=event)

    def loop(self):
        while True:
            self.conn.verifyToken(SkypeConnection.Auth.SkypeToken)
            self.cycle()

    def send_direct_message(self, user_id, message: str):
        self.contacts[user_id].chat.sendMsg(message)

    def send_direct_response(self, message: str):
        self.__current_event.msg.user.chat.sendMsg(message)

    def send_group_response(self, message: str):
        self.__current_event.msg.chat.sendMsg(message)

    def __process_message_event(self, event):
        keyword = self.__get_keyword(event=event)
        handler = self._handlers.get(keyword)

        if not handler:
            return

        try:
            self.__current_event = event
            self.__current_handler = handler
            handler.handle(event=event)
        except Exception as ex:
            self.__send_help_message(exception=ex)
        finally:
            self.__current_event = None
            self.__current_handler = None

    def __send_help_message(self, exception):
        message = self.__current_handler.help_message()
        message += '\n\nException:\n' + str(exception)

        self.send_direct_response(message)
        logger.warning(message)

    def __add_client_to_plugins(self, plugins: List[PluginBase]):
        for plugin in plugins:
            plugin.set_client(self)

    @staticmethod
    def __generate_handlers(plugins: List[PluginBase]):
        for plugin in plugins:
            for keyword in plugin.keywords():
                yield (keyword.lower(), plugin)

    @staticmethod
    def __get_keyword(event):
        msg_text = event.msg.content

        if not msg_text:
            return "", False

        msg_text = msg_text.strip()

        if not msg_text.startswith('#'):
            return "", False

        if isinstance(event, SkypeEditMessageEvent):
            idx = msg_text.rfind("<e_m")

            if idx != -1:
                msg_text = msg_text[:idx]

        msg_text = msg_text.lower()
        msg_text = msg_text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        lines = msg_text.split()

        return lines[0][1:]
