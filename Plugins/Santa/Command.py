class Command:
    def __init__(self):
        self.help = False
        self.participate = False
        self.start = False
        self.stop = False
        self.status = False

    def _set_help(self, value):
        self.help = True

    def _set_participate(self, value):
        self.participate = True

    def _set_start(self, value):
        self.start = True

    def _set_stop(self, value):
        self.stop = True

    def _set_status(self, value):
        self.status = True

    def _known_commands(self):
        return {
            "#help": self._set_help,
            "#bylemgrzeczny": self._set_participate,
            "#start": self._set_start,
            "#stop": self._set_stop,
            "#status": self._set_status,
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

    @classmethod
    def parse(cls, message):
        result = Command()

        message = result._prepare_message(message=message)

        result._parse_known_commands(message=message)

        return result

