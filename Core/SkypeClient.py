import logging
from datetime import datetime, timedelta
from time import sleep

from requests import ReadTimeout
from skpy import SkypeEventLoop, SkypeMessageEvent, SkypeEditMessageEvent, \
    SkypeAuthException, SkypeApiException, SkypeConnection, SkypeUtils

logger = logging.getLogger(__name__)


class SkypeClient(SkypeEventLoop):
    def __init__(self, username: str, password: str, token_file: str):
        super().__init__()

        self._handlers = None

        self.__username = username
        self.__password = password
        self.__token_file = token_file
        self.__token_expiration_buffer = timedelta(minutes=5)
        self.__current_event = None
        self.__current_handler = None

    def register_plugins(self, plugins):
        self._handlers = dict(self.__generate_handlers(plugins=plugins))

    def setPresence(self, *args, **kwargs):
        self.conn.syncEndpoints()
        self.__set_active()
        super().setPresence(*args, **kwargs)

    def onEvent(self, event):
        is_message_event = isinstance(event, SkypeMessageEvent)
        is_bots_message = is_message_event and event.msg.userId == self.userId

        if is_message_event and not is_bots_message:
            self.__process_message_event(event=event)

    def loop(self):
        self.__connect()

        while True:
            try:
                if not self.__verify_tokens():
                    logger.info("Tokens expired, reconnecting...")
                    self.__clear_token_file()
                    self.__connect()

                self.cycle()
            except (SkypeAuthException, SkypeApiException, ReadTimeout, Exception) as ex:
                logger.exception("%s raised", ex.__class__.__name__)
                logger.debug("Waiting 3 sec before retry...")
                sleep(3)
            except:
                logger.exception("Non-exception raised")
                raise

    def send_direct_message(self, user_id, message: str, me=False, rich=False):
        self.contacts[user_id].chat.sendMsg(content=message, me=me, rich=rich)

    def send_direct_response(self, message: str, me=False, rich=False):
        self.__current_event.msg.user.chat.sendMsg(content=message, me=me, rich=rich)

    def send_group_response(self, message: str, me=False, rich=False):
        self.__current_event.msg.chat.sendMsg(content=message, me=me, rich=rich)

    def __verify_tokens(self) -> bool:
        offset_datetime = datetime.now() + self.__token_expiration_buffer
        is_skype_token_valid = "skype" in self.conn.tokenExpiry and offset_datetime < self.conn.tokenExpiry["skype"]
        is_reg_token_valid = "reg" in self.conn.tokenExpiry and offset_datetime < self.conn.tokenExpiry["reg"]

        return is_skype_token_valid and is_reg_token_valid

    def __clear_token_file(self):
        with open(self.__token_file, 'w') as token_file:
            token_file.truncate(0)

    def __connect(self):
        super(SkypeClient, self).__init__(
            user=self.__username,
            pwd=self.__password,
            tokenFile=self.__token_file,
            status=SkypeUtils.Status.Online
        )

    def __set_active(self):
        self.conn("POST", "{0}/users/ME/endpoints/{1}/active".format(self.conn.msgsHost, self.conn.endpoints["all"][0].id),
                  auth=SkypeConnection.Auth.RegToken, json={"timeout": 120})

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
        logger.error(str(exception))

    @staticmethod
    def __generate_handlers(plugins):
        for plugin in plugins:
            for keyword in plugin.keywords():
                yield keyword.lower(), plugin

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
