from skpy import SkypeNewMessageEvent

from Core.PluginBase import PluginBase


class PizzaPlugin(PluginBase):
    def friendly_name(self):
        return 'Pizza plugin'

    def version(self):
        return '0.1'

    def keywords(self):
        return ['pizza']

    def handle(self, event):
        return

    def help_message(self):
        return """{friendly_name} v{version}

Keywords: {keywords}
Commands:
    #start
    #stop
    #cost
    NUMBER_OF_PIECES
""".format(friendly_name=self.friendly_name(),
           version=self.version(),
           keywords=','.join(['#' + keyword for keyword in self.keywords()])
           )