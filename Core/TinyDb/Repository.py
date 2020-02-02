import urllib.parse
from abc import ABC, abstractmethod
from typing import List, Optional

from skpy import SkypeUser, SkypeChat
from tinydb import TinyDB, Query

from Core.TinyDb.ModelBase import ModelBase


class Repository(ABC):
    @property
    @abstractmethod
    def MODEL_CLASS(self) -> type:
        pass

    def __init__(self, database: TinyDB, table_prefix: str):
        self._database = database
        self._table = database.table(urllib.parse.quote("%s_%s" % (table_prefix, type(self).__name__)))

    def insert(self, model: ModelBase):
        model.doc_id = self._table.insert(model)

    def remove(self, model: ModelBase):
        self._table.remove(doc_ids=[model.doc_id])

    def remove_all(self, chat: SkypeChat):
        self._table.remove(Query().chat_id == chat.id)

    def find_all(self, chat: SkypeChat) -> List[ModelBase]:
        query = Query()
        docs = self._table.search(query.chat_id == chat.id)

        return [self.MODEL_CLASS().fill(doc=doc) for doc in docs]

    def find_all_user(self, user: SkypeUser, chat: SkypeChat) -> List[ModelBase]:
        query = Query()
        docs = self._table.search((query.user_id == user.id) & (query.chat_id == chat.id))

        return [self.MODEL_CLASS().fill(doc=doc) for doc in docs]

    def find_single(self, chat: SkypeChat) -> Optional[ModelBase]:
        objects = self.find_all(chat=chat)

        if len(objects) == 0:
            return None
        elif len(objects) == 1:
            return objects[0]
        else:
            raise EnvironmentError("Multiple objects found at chat(%s)" % chat.id)

    def find_single_user(self, user: SkypeUser, chat: SkypeChat) -> Optional[ModelBase]:
        objects = self.find_all_user(user=user, chat=chat)

        if len(objects) == 0:
            return None
        elif len(objects) == 1:
            return objects[0]
        else:
            raise EnvironmentError("Multiple objects found for user (%s) at chat(%s)" % (user.id, chat.id))
