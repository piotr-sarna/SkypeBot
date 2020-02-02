import json
from abc import ABC, abstractmethod

from tinydb_serialization import Serializer


class JsonSerializer(Serializer, ABC):
    @property
    @abstractmethod
    def OBJ_CLASS(self):
        pass

    def encode(self, obj):
        obj_dict = {k: v for k, v in obj.__dict__.items() if v is not None}
        return json.dumps(obj_dict)

    def decode(self, s):
        obj = self.OBJ_CLASS()
        obj.__dict__.update(json.loads(s))

        return obj
