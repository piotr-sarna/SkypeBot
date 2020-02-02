from skpy import SkypeUser

from Core.TinyDb.Serializers.JsonSerializer import JsonSerializer


class SkypeUserNameSerializer(JsonSerializer):
    OBJ_CLASS = SkypeUser.Name
