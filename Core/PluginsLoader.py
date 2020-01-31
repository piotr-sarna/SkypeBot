import inspect
import importlib
import pkgutil
import logging

import Plugins

from .PluginBase import PluginBase

logger = logging.getLogger(__name__)


class PluginsLoader:
    @staticmethod
    def __iterate_namespace(namespace):
        return pkgutil.iter_modules(namespace.__path__, namespace.__name__ + ".")

    @staticmethod
    def __get_plugin_class(module_name):
        module_instance = importlib.import_module(module_name)
        plugin_classes = inspect.getmembers(module_instance, inspect.isclass)

        if len(plugin_classes) != 1:
            logger.critical("Plugin module must import exactly one class. Module name: '%s'", module_name)
            exit(-1)

        plugin_class = plugin_classes[0][1]

        if not issubclass(plugin_class, PluginBase):
            logger.critical("Plugin class must inherit from IBotPlugin. Module name: '%s'", module_name)
            exit(-1)

        return plugin_class

    @staticmethod
    def __read_plugins_namespace():
        for _, module_name, is_package in PluginsLoader.__iterate_namespace(Plugins):
            if not is_package:
                continue

            yield PluginsLoader.__get_plugin_class(module_name)

    @staticmethod
    def __validate_keywords_unique(plugins):
        keywords = []

        for plugin in plugins:
            keywords.extend([keyword.lower() for keyword in plugin.keywords()])

        unique_keywords = list(set(keywords))

        if len(keywords) != len(unique_keywords):
            logger.critical("Plugins\' keywords conflict. Loaded keywords: %s", str.join(', ', sorted(keywords)))
            exit(-1)

    @staticmethod
    def load():
        plugins = [plugin() for plugin in PluginsLoader.__read_plugins_namespace()]

        PluginsLoader.__validate_keywords_unique(plugins)

        return plugins
