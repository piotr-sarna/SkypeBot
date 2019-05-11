
class Command:
    def __init__(self):
        self.help = False
        self.blik = None
        self.account_number = None
        self.account_owner_name = None
        self.transfer_title = None
        self.delivery_cost = 0
        self.order_costs = {}

    def _set_help(self, value):
        self.help = True

    def _set_blik(self, value):
        self.blik = value

    def _account_number(self, value):
        self.account_number = value

    def _account_owner_name(self, value):
        self.account_owner_name = value

    def _transfer_title(self, value):
        self.transfer_title = value

    def _delivery_cost(self, value):
        self.delivery_cost = int(float(value.replace(',', '.'))*100)

    def _known_commands(self):
        return {
            "#help": self._set_help,
            "#blik": self._set_blik,
            "#acc_number": self._account_number,
            "#acc_name": self._account_owner_name,
            "#title": self._transfer_title,
            "#delivery": self._delivery_cost,
        }

    def _prepare_message(self, message):
        message = message.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()
        message = message.replace("@", "\n@")

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

    def _parse_users_orders(self, message):
        for line in message.splitlines():
            line = line.strip()

            if line.startswith("@"):
                user_id, amount = self._parse_order_cost(line)

                self.order_costs[user_id] = amount

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
        result._parse_users_orders(message=message)

        return result
