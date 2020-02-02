from Core.TinyDb.ModelBase import ModelBase


class Order(ModelBase):
    def to_order(self):
        return self
