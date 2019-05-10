from skpy import SkypeEventLoop, SkypeNewMessageEvent


class SkypeListener(SkypeEventLoop):

    def __init__(self, username, password):
        super(SkypeListener, self).__init__(username, password)

    def configure_plugins(self):
        pass

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent) and not event.msg.userId == self.userId:
            event.msg.chat.sendMsg("Simple response")
