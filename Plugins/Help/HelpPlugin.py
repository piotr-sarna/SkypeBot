from skpy import SkypeNewMessageEvent

from Core.PluginBase import PluginBase
from Plugins.Help.Messages import Messages


class HelpPlugin(PluginBase):
    def friendly_name(self):
        return 'Skype Bot'

    def version(self):
        from version import __version__
        return __version__

    def keywords(self):
        return ['help']

    def handle(self, event):
        if not isinstance(event, SkypeNewMessageEvent):
            return

        self.client.send_direct_response(self.help_message())

    def help_message(self):
        return Messages(self).help_message(self.client._handlers)
