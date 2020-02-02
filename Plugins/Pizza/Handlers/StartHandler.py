from Plugins.Pizza.Handlers.HandlerBase import HandlerBase
from Plugins.Pizza.Messages import Messages
from Plugins.Pizza.Model.Organizer import Organizer


class StartHandler(HandlerBase):
    def handle(self):
        organizer = self._organizers.find_single(chat=self._chat)

        if organizer:
            raise Exception(Messages().error_only_one_pizza())

        organizer = Organizer().with_context(user=self._user, chat=self._chat)
        self._organizers.insert(model=organizer)

        self._orders.remove_all(chat=self._chat)
        self._optional_orders.remove_all(chat=self._chat)
        self._forced_orders.remove_all(chat=self._chat)

        self._client.send_direct_response(Messages().start_direct(self._message.time))
        self._client.send_group_response(Messages().start_group(organizer))
