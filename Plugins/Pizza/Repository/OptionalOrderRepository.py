from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.OptionalOrder import OptionalOrder


class OptionalOrderRepository(Repository):
    MODEL_CLASS = OptionalOrder
