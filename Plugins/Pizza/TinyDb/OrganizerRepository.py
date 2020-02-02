from typing import List

from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Dao.OrganizerDao import OrganizerDao


class OrganizerRepository(Repository):
    def insert(self, organizer: OrganizerDao):
        organizer.doc_id = self._table.insert(organizer)

    def find_all(self) -> List[OrganizerDao]:
        return [OrganizerDao().fill(doc=doc) for doc in self._table.all()]
