
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
        resolvers = {
            "#help": result._set_help,
            "#blik": result._set_blik,
            "#acc_number": result._account_number,
            "#acc_name": result._account_owner_name,
            "#title": result._transfer_title,
            "#delivery": result._delivery_cost,
        }
        lines = [line.strip() for line in message.splitlines()]

        for line in lines:
            if line.startswith("@"):
                user_id, amount = cls._parse_order_cost(line)

                result.order_costs[user_id] = amount
            else:
                for key, resolver in resolvers.items():
                    if line.startswith(key):
                        value = line[len(key):].strip()
                        resolver(value=value)
                        break

        return result
