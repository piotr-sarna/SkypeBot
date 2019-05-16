
class Command:
    def __init__(self):
        self.help = False
        self.number_of_slices = None
        self.start = False
        self.stop = False
        self.cost = None

    def _set_help(self, value):
        self.help = True

    def _set_number_of_slices(self, value):
        if value:
            self.number_of_slices = abs(int(value))

    def _set_start(self, value):
        self.start = True

    def _set_stop(self, value):
        self.stop = True

    def _set_cost(self, value):
        self.cost = int(float(value.replace(',', '.'))*100)

    def _known_commands(self):
        return {
            "#help": self._set_help,
            "#pizza": self._set_number_of_slices,
            "#start": self._set_start,
            "#stop": self._set_stop,
            "#cost": self._set_cost,
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

    @staticmethod
    def _parse_order_cost(line):
        split_line = line.split(" ", 1)
        user_id = split_line[0].strip()[1:]
        amount = split_line[1].strip().replace(',', '.')
        amount = int(float(amount) * 100)

        return user_id, amount

    @classmethod
    def parse(cls, message):
        result = Command()

        message = result._prepare_message(message=message)

        result._parse_known_commands(message=message)

        return result
