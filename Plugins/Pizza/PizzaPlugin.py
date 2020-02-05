from skpy import SkypeNewMessageEvent, SkypeEditMessageEvent

from Core.PluginBase import PluginBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Repository.ForcedOrderRepository import ForcedOrderRepository
from Plugins.Pizza.Repository.OptionalOrderRepository import OptionalOrderRepository
from Plugins.Pizza.Repository.OrderRepository import OrderRepository
from Plugins.Pizza.Repository.OrganizerRepository import OrganizerRepository
from Plugins.Pizza.Repository.Repositories import Repositories
from .Command import Command


class PizzaPlugin(PluginBase):
    def __init__(self, client, database):
        super(PizzaPlugin, self).__init__(client=client, database=database)

        self.repositories = Repositories(
            organizer=OrganizerRepository(database=database, table_prefix=self.friendly_name()),
            order=OrderRepository(database=database, table_prefix=self.friendly_name()),
            optional_order=OptionalOrderRepository(database=database, table_prefix=self.friendly_name()),
            forced_order=ForcedOrderRepository(database=database, table_prefix=self.friendly_name())
        )

    def friendly_name(self):
        return 'Pizza plugin'

    def version(self):
        return '1.0.0-rc1'

    def keywords(self):
        return ['pizza']

    def help_message(self):
        return Messages.help(self)

    def handle(self, event):
        if not isinstance(event, SkypeNewMessageEvent) and not isinstance(event, SkypeEditMessageEvent):
            return

        message = event.msg
        command = Command.parse(message=message.markup)
        command.handle(plugin=self, message=message)
