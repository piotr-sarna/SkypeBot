from skpy import SkypeNewMessageEvent

from Core.PluginBase import PluginBase


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

        message = self.help_message()

        self._skype.contacts[event.msg.userId].chat.sendMsg(message)

    def help_message(self):
        all_handlers = self._skype._handlers
        registered_keywords = [keyword for keyword in all_handlers.keys() if keyword not in self.keywords()]
        registered_keywords = sorted(registered_keywords)
        plugin_line = ["    #{keyword} - {plugin_name}".format(keyword=keyword, plugin_name=all_handlers[keyword].friendly_name())
                       for keyword in registered_keywords]

        return """{friendly_name} v{version}

Available plugins:
{plugins_lines}""".format(friendly_name=self.friendly_name(),
                          version=self.version(),
                          plugins_lines='\n'.join(plugin_line)
                          )
