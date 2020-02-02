from skpy import SkypeUser
from tinydb.database import Document

from Core.TinyDb.DaoBase import DaoBase


class OrganizerDao(DaoBase):
    def __init__(self):
        super(OrganizerDao, self).__init__()

        self.user_id = None
        self.user_name = None

    def from_user(self, user: SkypeUser):
        self.user_id = user.id
        self.user_name = user.name
        return self

    def fill(self, doc: Document):
        super(OrganizerDao, self).fill(doc=doc)
        self.user_id = doc['user_id']
        self.user_name = doc['user_name']
        return self
