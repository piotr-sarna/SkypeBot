import inspect
import importlib
import pkgutil
import logging

import Plugins

from .PluginBase import PluginBase

logger = logging.getLogger(__name__)


class PluginsLoader:
    def __init__(self):
        pass

    @staticmethod
    def __iter_namespace(ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    def load(self):
        result = []

        for _, name, is_pkg in self.__iter_namespace(Plugins):
            if not is_pkg:
                continue

            module = importlib.import_module(name)
            plugin_classes = inspect.getmembers(module, inspect.isclass)

            if len(plugin_classes) != 1:
                logger.warning("Plugin module must import exactly one class. Module name: '%s'", name)
                continue

            plugin_class = plugin_classes[0][1]

            if not issubclass(plugin_class, PluginBase):
                logger.warning("Plugin class must inherit from IBotPlugin. Module name: '%s'", name)
                continue

            result.append(plugin_class)

        return result
