from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.OptionalOrder import OptionalOrder


class ForcedOrderRepository(Repository):
    MODEL_CLASS = OptionalOrder
