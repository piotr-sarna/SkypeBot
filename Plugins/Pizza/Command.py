from skpy import SkypeMsg

from Plugins.Pizza import PizzaPlugin
from Plugins.Pizza.Handlers.HelpHandler import HelpHandler
from Plugins.Pizza.Handlers.OptionalSlicesHandler import OptionalSlicesHandler
from Plugins.Pizza.Handlers.SlicesHandler import SlicesHandler
from Plugins.Pizza.Handlers.StartHandler import StartHandler
from Plugins.Pizza.Handlers.StatusHandler import StatusHandler
from Plugins.Pizza.Handlers.StopHandler import StopHandler


class Command:
    def __init__(self):
        self.help = False
        self.number_of_slices = None
        self.optional_slices = None
        self.start = False
        self.stop = False
        self.status = False

    @classmethod
    def parse(cls, message):
        result = Command()

        message = result._prepare_message(message=message)

        result._parse_known_commands(message=message)
        result._validate()

        return result

    def handle(self, plugin: PizzaPlugin, message: SkypeMsg):
        if self.help:
            HelpHandler(plugin=plugin, message=message).handle()
            return

        if self.start:
            StartHandler(plugin=plugin, message=message).handle()
        elif self.stop:
            StopHandler(plugin=plugin, message=message).handle()
        elif self.number_of_slices is not None:
            SlicesHandler(plugin=plugin, message=message, slices=self.number_of_slices).handle()
        elif self.optional_slices is not None:
            OptionalSlicesHandler(plugin=plugin, message=message, slices=self.optional_slices).handle()
        elif self.status:
            StatusHandler(plugin=plugin, message=message).handle()

    def _set_help(self, value):
        self.help = True

    def _set_number_of_slices(self, value):
        if not value:
            return

        try:
            value = int(value)

            if not (0 <= value <= 8):
                raise ValueError("Value out of range")
        except ValueError as ex:
            raise ValueError("Number of slices must be an integer between 0 and 8. Inner reason: \"" + str(ex) + "\"")

        self.number_of_slices = value

    def _set_start(self, value):
        self.start = True

    def _set_stop(self, value):
        self.stop = True

    def _set_status(self, value):
        self.status = True

    def _set_optional_slices(self, value):
        if not value:
            return

        try:
            value = int(value)

            if not (0 <= value <= 7):
                raise ValueError("Value out of range")
        except ValueError as ex:
            raise ValueError("Number of optional slices must be an integer between 0 and 7. Inner reason: \"" + str(ex) + "\"")

        self.optional_slices = value

    def _known_commands(self):
        return {
            "#help": self._set_help,
            "#pizza": self._set_number_of_slices,
            "#start": self._set_start,
            "#stop": self._set_stop,
            "#status": self._set_status,
            "#optional": self._set_optional_slices,
        }

    def _prepare_message(self, message):
        idx = message.rfind("<e_m")

        if idx != -1:
            message = message[:idx]

        message = message.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()

        for command in self._known_commands().keys():
            message = message.replace(command, "\n" + command)

        return message

    def _parse_known_commands(self, message):
        for line in message.splitlines():
            line = line.strip()

            if not line.startswith("#"):
                continue

            for command, resolver in self._known_commands().items():
                if line.startswith(command):
                    value = line[len(command):].strip()
                    resolver(value=value)
                    break

    def _validate(self):
        commands_number = 0
        commands_number += 1 if self.start else 0
        commands_number += 1 if self.stop else 0
        commands_number += 1 if self.number_of_slices is not None else 0
        commands_number += 1 if self.optional_slices is not None else 0
        commands_number += 1 if self.status else 0

        if commands_number == 0:
            self.help = True
        elif commands_number != 1:
            raise Exception("You have to specify exactly one command at once")
