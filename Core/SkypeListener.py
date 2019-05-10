from skpy import SkypeEventLoop, SkypeNewMessageEvent


class SkypeListener(SkypeEventLoop):

    def __init__(self, username, password, plugins):
        super(SkypeListener, self).__init__(username, password)

        self._handlers = self._prepare_handlers(plugins=plugins)

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent) and not event.msg.userId == self.userId:
            keyword = self._get_keyword(event.msg.markup)

            if keyword and keyword in self._handlers:
                handler = self._handlers[keyword]
                try:
                    handler.handle(event.msg)
                except Exception as e:
                    message = handler.help_message() + '\n\nException:\n' + str(e)
                    self.contacts[event.msg.userId].chat.sendMsg(message)
                    print message

    def _prepare_handlers(self, plugins):
        result = {}
        plugins_objs = [plugin(self) for plugin in plugins]

        for plugin in plugins_objs:
            for keyword in plugin.keywords():
                keyword = keyword.lower()

                if keyword in result:
                    print 'Plugins\' keywords conflict for \'' + keyword + '\''
                    exit(-1)

                result[keyword] = plugin

        return result

    @staticmethod
    def _get_keyword(msg_text):
        first_line = msg_text.splitlines()[0]
        first_line = first_line.strip()
        first_line = first_line.lower()

        if first_line.startswith('#'):
            return first_line[1:]
        else:
            return None
