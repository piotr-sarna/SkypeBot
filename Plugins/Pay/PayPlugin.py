from Core.IBotPlugin import IBotPlugin


class PayPlugin(IBotPlugin):
    def keywords(self):
        return ['pay']

    def handle(self, message):
        pass
