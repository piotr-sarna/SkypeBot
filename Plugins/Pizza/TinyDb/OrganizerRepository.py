from typing import Optional

from skpy import SkypeChat
from tinydb import Query

from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.Organizer import Organizer


class OrganizerRepository(Repository):
    def find_single_at_chat(self, chat: SkypeChat) -> Optional[Organizer]:
        organizer_query = Query()
        doc = self._table.search(organizer_query.chat_id == chat.id)

        if len(doc) == 0:
            return None
        elif len(doc) == 1:
            return Organizer().fill(doc=doc[0])
        else:
            raise EnvironmentError("Multiple organizers at one chat")

    def insert(self, organizer: Organizer):
        organizer.doc_id = self._table.insert(organizer)

    def remove(self, organizer: Organizer):
        self._table.remove(doc_ids=[organizer.doc_id])
