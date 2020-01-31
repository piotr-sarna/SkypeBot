from typing import Dict

from Core.PluginBase import PluginBase

HELP_MESSAGE_TEMPLATE = """{friendly_name} v{version}

Available plugins:
{plugins_entries}"""
PLUGIN_ENTRY_TEMPLATE = "    #{keyword} - {plugin_name}"


class Messages:
    def __init__(self, help_plugin: PluginBase):
        self.__help_plugin = help_plugin

    def help_message(self, all_plugins: Dict[str, PluginBase]) -> str:
        other_plugins_keywords = [keyword for keyword in all_plugins.keys() if keyword not in self.__help_plugin.keywords()]
        other_plugins_keywords = sorted(other_plugins_keywords)

        plugin_entries = [
            PLUGIN_ENTRY_TEMPLATE.format(keyword=keyword, plugin_name=all_plugins[keyword].friendly_name())
            for keyword in other_plugins_keywords
        ]

        return HELP_MESSAGE_TEMPLATE.format(
            friendly_name=self.__help_plugin.friendly_name(),
            version=self.__help_plugin.version(),
            plugins_entries='\n'.join(plugin_entries)
        )
