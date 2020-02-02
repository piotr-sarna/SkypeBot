from datetime import datetime
from typing import List

from skpy import SkypeUser

from Core.PluginBase import PluginBase
from Plugins.Pizza.Model.Organizer import Organizer

ERROR_NOT_STARTED = "No #pizza is currently started"
ERROR_ONLY_ONE_PIZZA = "Exactly one #pizza can be started at the same time"
ERROR_ONLY_OWNER_CAN_STOP = "Only user which started #pizza can stop it"
WHATEVER_MESSAGE = "¯\_(ツ)_/¯"
HELP_MESSAGE_TEMPLATE = """{friendly_name} v{version}

Keywords: {keywords}
Commands:
    #help
    #start
    #stop
    #status
    NUMBER_OF_SLICES
"""
START_DIRECT_MESSAGE_TEMPLATE = "You've started #pizza at {time} UTC. Please remember to #pizza #stop"
START_GROUP_MESSAGE_TEMPLATE = "#pizza started by {user_name} ({user_id})"
STOP_DIRECT_MESSAGE_TEMPLATE = """You've stopped #pizza at {time} UTC.

Summary:
#pizza(s) to order: {pizzas}
{orders}
"""
STOP_GROUP_MESSAGE_TEMPLATE = """Summary for #pizza started by {user_name} ({user_id}):
#pizza(s) to order: {pizzas}

{orders}"""
SLICES_NUMBER_DIRECT_MESSAGE_TEMPLATE = "You've registered for {slices_number} #pizza slice(s)"
SLICES_NUMBER_GROUP_MESSAGE_TEMPLATE = "{pizzas} #pizza(s) to order, {missing_slices} slice(s) are missing for the next #pizza"
STATUS_MESSAGE_TEMPLATE = """Started by {user_name} ({user_id})
Total #pizza(s) to order: {number_of_pizzas}
Slice(s) missing for the next #pizza: {missing_slices}

#pizza participants:
{orders_summaries}

#pizza reserve list:
{overflow_summaries}
"""
ORDER_MESSAGE_TEMPLATE = "{user_name} ({user_id}) - {slices}"
ORDER_REDUCED_MESSAGE_TEMPLATE = "Sorry, your #pizza order was reduced to {slices} slice(s), because of rounding to whole #pizza(s) :("
ORDER_REMOVED_MESSAGE = "Sorry, you were removed from #pizza order, because of rounding to whole #pizza(s) :("


class Messages:
    def __init__(self, pizza_plugin: PluginBase):
        self.__pizza_plugin = pizza_plugin

    def help(self) -> str:
        return HELP_MESSAGE_TEMPLATE.format(
            friendly_name=self.__pizza_plugin.friendly_name(),
            version=self.__pizza_plugin.version(),
            keywords=','.join(['#' + keyword for keyword in self.__pizza_plugin.keywords()])
        )

    def start_direct(self, start_time: datetime) -> str:
        return START_DIRECT_MESSAGE_TEMPLATE.format(time=str(start_time.replace(microsecond=0)))

    def start_group(self, organizer: Organizer) -> str:
        return START_GROUP_MESSAGE_TEMPLATE.format(user_name=organizer.user_name, user_id=organizer.user_id)

    def stop_direct(self, stop_time: datetime, pizzas: int, orders: List[str]) -> str:
        return STOP_DIRECT_MESSAGE_TEMPLATE.format(
            time=str(stop_time.replace(microsecond=0)),
            pizzas=pizzas,
            orders="\n".join(orders)
        )

    def stop_group(self, organizer: Organizer, pizzas: int, orders: List[str]) -> str:
        return STOP_GROUP_MESSAGE_TEMPLATE.format(
            user_name=organizer.user_name,
            user_id=organizer.user_id,
            pizzas=pizzas,
            orders="\n".join(orders)
        )

    def slices_direct(self, slices_number: int) -> str:
        return SLICES_NUMBER_DIRECT_MESSAGE_TEMPLATE.format(slices_number=slices_number)

    def slices_group(self, pizzas: int, missing_slices: int) -> str:
        return SLICES_NUMBER_GROUP_MESSAGE_TEMPLATE.format(pizzas=pizzas, missing_slices=missing_slices)

    def status(self, organizer: Organizer, pizzas: int, missing_slices: int, orders: List[str], overflows: List[str]) -> str:
        return STATUS_MESSAGE_TEMPLATE.format(
            user_name=organizer.user_name,
            user_id=organizer.user_id,
            number_of_pizzas=pizzas,
            missing_slices=missing_slices,
            orders_summaries="\n".join(orders) if len(orders) else WHATEVER_MESSAGE,
            overflow_summaries="\n".join(overflows) if len(overflows) else WHATEVER_MESSAGE,
        )

    def order(self, user: SkypeUser, slices: int) -> str:
        return ORDER_MESSAGE_TEMPLATE.format(
            user_name=user.name,
            user_id=user.id,
            slices=slices
        )

    def order_reduced(self, slices: int) -> str:
        return ORDER_REDUCED_MESSAGE_TEMPLATE.format(
            slices=slices
        )

    def order_removed(self) -> str:
        return ORDER_REMOVED_MESSAGE

    def error_not_started(self) -> str:
        return ERROR_NOT_STARTED

    def error_only_one_pizza(self) -> str:
        return ERROR_ONLY_ONE_PIZZA

    def error_only_owner_can_stop(self) -> str:
        return ERROR_ONLY_OWNER_CAN_STOP