from skpy import SkypeEventLoop, SkypeMessageEvent, SkypeEditMessageEvent


class SkypeListener(SkypeEventLoop):
    def __init__(self, username, password, plugins):
        super(SkypeListener, self).__init__(username, password)

        self._handlers = self._prepare_handlers(plugins=plugins)

    def onEvent(self, event):
        is_message_event = isinstance(event, SkypeMessageEvent)
        is_bots_message = is_message_event and event.msg.userId == self.userId

        if is_message_event and not is_bots_message:
            self._process_message_event(event=event)

    def _process_message_event(self, event):
        keyword, is_single_command = self._get_keyword(event=event)
        handler = self._handlers.get(keyword)

        if not handler:
            return

        if is_single_command:
            self._send_help_message(event=event, handler=handler)
            return

        try:
            handler.handle(event=event)
        except Exception as e:
            self._send_help_message(event=event, handler=handler, exception=e)

    def _send_help_message(self, event, handler, exception=None):
        message = handler.help_message()

        if exception:
            message += '\n\nException:\n' + str(exception)

        self.contacts[event.msg.userId].chat.sendMsg(message)
        print(message)

    def _prepare_handlers(self, plugins):
        result = {}
        plugins_objs = [plugin(self) for plugin in plugins]

        for plugin in plugins_objs:
            for keyword in plugin.keywords():
                keyword = keyword.lower()

                if keyword in result:
                    print('Plugins\' keywords conflict for \'' + keyword + '\'')
                    exit(-1)

                result[keyword] = plugin

        return result

    @staticmethod
    def _get_keyword(event):
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

        return lines[0][1:], len(lines) == 1
