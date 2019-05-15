from skpy import SkypeNewMessageEvent, SkypeEditMessageEvent

from Core.PluginBase import PluginBase
from .Command import Command


class PizzaPlugin(PluginBase):
    def __init__(self, skype):
        super(PizzaPlugin, self).__init__(skype=skype)
        self._orders = []
        self._started_by = None
        self._is_stopped = False

    def friendly_name(self):
        return 'Pizza plugin'

    def version(self):
        return '0.1'

    def keywords(self):
        return ['pizza']

    def handle(self, event):
        if not isinstance(event, SkypeNewMessageEvent) and not isinstance(event, SkypeEditMessageEvent):
            return

        message = event.msg
        command = Command.parse(message=message.markup)

        if self._process_if_help_command(message=message, command=command):
            return

        self._ensure_exactly_one_command_is_given(command=command)

        if command.start:
            self._handle_start(message=message, command=command)
        elif command.stop:
            self._handle_stop(message=message, command=command)
        elif command.cost:
            self._handle_cost(message=message, command=command)
        elif command.number_of_pieces:
            self._handle_number_of_pieces(message=message, command=command)

    def help_message(self):
        return """{friendly_name} v{version}

Keywords: {keywords}
Commands:
    #help
    #start
    #stop
    #cost
    NUMBER_OF_PIECES
""".format(friendly_name=self.friendly_name(),
           version=self.version(),
           keywords=','.join(['#' + keyword for keyword in self.keywords()])
           )

    def _process_if_help_command(self, message, command):
        if command.help:
            self._skype.contacts[message.userId].chat.sendMsg(self.help_message())

        return command.help

    @staticmethod
    def _ensure_exactly_one_command_is_given(command):
        commands_number = 0
        commands_number += 1 if command.start else 0
        commands_number += 1 if command.stop else 0
        commands_number += 1 if command.cost else 0
        commands_number += 1 if command.number_of_pieces else 0

        if commands_number != 1:
            raise Exception("You have to specify exactly one command at once")

    def _handle_start(self, message, command):
        if self._started_by:
            raise Exception("Exactly one #pizza can be started at the same time")

        self._orders = []
        self._started_by = message.userId
        self._is_stopped = False

        self._skype.contacts[message.userId].chat.sendMsg("OK")

    def _handle_stop(self, message, command):
        if not self._started_by:
            raise Exception("No #pizza is currently started")

        if self._started_by != message.userId:
            raise Exception("Only user which started #pizza can stop it")

        if self._is_stopped:
            raise Exception("#pizza is already stopped")

        self._is_stopped = True

        # TODO: send summary to _started_by
        # TODO: inform users that does not fit into order

        self._skype.contacts[message.userId].chat.sendMsg("OK")

    def _handle_cost(self, message, command):
        pass

    def _handle_number_of_pieces(self, message, command):
        if not self._started_by or self._is_stopped:
            raise Exception("No #pizza is currently started")

        existing_idx = [i for i, v in enumerate(self._orders) if v[0] == message.userId]

        if existing_idx:
            self._orders.pop(existing_idx[0])

        self._orders.append((message.userId, command.number_of_pieces))
