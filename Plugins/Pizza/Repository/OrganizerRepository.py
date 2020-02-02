from typing import Optional

from skpy import SkypeChat

from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.Organizer import Organizer


class OrganizerRepository(Repository):
    MODEL_CLASS = Organizer

    def find_single(self, chat: SkypeChat) -> Optional[Organizer]:
        return super(OrganizerRepository, self).find_single(chat=chat)
