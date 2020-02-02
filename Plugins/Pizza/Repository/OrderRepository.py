from Core.TinyDb.Repository import Repository
from Plugins.Pizza.Model.Order import Order


class OrderRepository(Repository):
    MODEL_CLASS = Order
