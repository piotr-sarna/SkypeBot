from abc import ABC
from collections.abc import Mapping
from datetime import datetime

from tinydb.database import Document


class DaoBase(Mapping, ABC):
    def __getitem__(self, k):
        return self.__dict__.__getitem__(k)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __len__(self):
        return self.__dict__.__len__()

    def __init__(self):
        super(DaoBase, self).__init__()

        self.doc_id = None
        self.type = type(self).__name__
        self.created_at = datetime.now()

    def fill(self, doc: Document):
        self.doc_id = doc.doc_id
        self.type = doc['type']
        self.created_at = doc['created_at']
        return self
