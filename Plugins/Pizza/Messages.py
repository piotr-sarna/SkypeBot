from datetime import datetime
from typing import List, Optional

from Core.PluginBase import PluginBase
from Plugins.Pizza.Model.Order import Order
from Plugins.Pizza.Model.Organizer import Organizer
from Plugins.Pizza.Utils.PizzaCalculator import OrderSummary

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
    #optional NUMBER_OF_SLICES
    NUMBER_OF_SLICES
"""
START_DIRECT_MESSAGE_TEMPLATE = "You've started #pizza at {time} UTC. Please remember to #pizza #stop"
START_GROUP_MESSAGE_TEMPLATE = "#pizza started by {user_name} ({user_id})"
STOP_LUCKY_MESSAGE_TEMPLATE = "Lucky #pizza slice for {lucky_name} ({lucky_id})"
STOP_DIRECT_MESSAGE_TEMPLATE = """You've stopped #pizza at {time} UTC.

Summary:
#pizza(s) to order: {pizzas}
{orders}"""
STOP_GROUP_MESSAGE_TEMPLATE = """Summary for #pizza started by {user_name} ({user_id}):
#pizza(s) to order: {pizzas}

Summary:
{orders}"""
SLICES_USER_STATUS_NORMAL_MESSAGE_TEMPLATE = "You've registered for {slices} #pizza slice(s)"
SLICES_USER_STATUS_FORCED_MESSAGE_TEMPLATE = """You've registered for {slices} #pizza slice(s). 
You've reduced your order, so it can be increased by up to {forced_slices} #pizza slice(s)."""
OPTIONAL_SLICES_USER_STATUS_NORMAL_MESSAGE_TEMPLATE = "You've registered for {slices} optional #pizza slice(s)"
SLICES_NUMBER_GROUP_MESSAGE_TEMPLATE = "{pizzas} #pizza(s) to order, {missing_slices} slice(s) are missing for the next #pizza"
STATUS_MESSAGE_TEMPLATE = """Started by {user_name} ({user_id})
Total #pizza(s) to order: {number_of_pizzas}
Slice(s) missing for the next #pizza: {missing_slices}

#pizza participants:
{orders_summaries}

reg - registered slice(s), opt - optional slice(s), rem - slice(s) requested to remove
"""
ORDER_MESSAGE_TEMPLATE = "{user_name} ({user_id}) - {slices}"
ORDER_REDUCED_MESSAGE_TEMPLATE = "Sorry, your #pizza order was reduced to {slices} slice(s), because of rounding to whole #pizza(s) :("
ORDER_REMOVED_MESSAGE = "Sorry, you were removed from #pizza order, because of rounding to whole #pizza(s) :("


class Messages:
    @staticmethod
    def help(plugin: PluginBase) -> str:
        return HELP_MESSAGE_TEMPLATE.format(
            friendly_name=plugin.friendly_name(),
            version=plugin.version(),
            keywords=','.join(['#' + keyword for keyword in plugin.keywords()])
        )

    @staticmethod
    def start_direct(start_time: datetime) -> str:
        return START_DIRECT_MESSAGE_TEMPLATE.format(time=str(start_time.replace(microsecond=0)))

    @staticmethod
    def start_group(organizer: Organizer) -> str:
        return START_GROUP_MESSAGE_TEMPLATE.format(user_name=organizer.user_name, user_id=organizer.user_id)

    @staticmethod
    def stop_direct(stop_time: datetime, pizzas: int, orders: List[str], lucky_order: Optional[Order]) -> str:
        standard_message = STOP_DIRECT_MESSAGE_TEMPLATE.format(
            time=str(stop_time.replace(microsecond=0)),
            pizzas=pizzas,
            orders="\n".join(orders) if orders else WHATEVER_MESSAGE
        )

        return standard_message \
            if not lucky_order \
            else standard_message + "\n\n" + STOP_LUCKY_MESSAGE_TEMPLATE.format(
                lucky_name=lucky_order.user_name,
                lucky_id=lucky_order.user_id
            )

    @staticmethod
    def stop_group(organizer: Organizer, pizzas: int, orders: List[str], lucky_order: Optional[Order]) -> str:
        standard_message = STOP_GROUP_MESSAGE_TEMPLATE.format(
            user_name=organizer.user_name,
            user_id=organizer.user_id,
            pizzas=pizzas,
            orders="\n".join(orders) if orders else WHATEVER_MESSAGE
        )

        return standard_message \
            if not lucky_order \
            else standard_message + "\n\n" + STOP_LUCKY_MESSAGE_TEMPLATE.format(
                lucky_name=lucky_order.user_name,
                lucky_id=lucky_order.user_id
            )

    @staticmethod
    def slices_user_status(slices: int, forced_slices: int = 0) -> str:
        if forced_slices != 0:
            return SLICES_USER_STATUS_FORCED_MESSAGE_TEMPLATE.format(slices=slices, forced_slices=forced_slices)
        else:
            return SLICES_USER_STATUS_NORMAL_MESSAGE_TEMPLATE.format(slices=slices)

    @staticmethod
    def slices_group(pizzas: int, missing_slices: int) -> str:
        return SLICES_NUMBER_GROUP_MESSAGE_TEMPLATE.format(pizzas=pizzas, missing_slices=missing_slices)

    @staticmethod
    def optional_slices_user_status(optional_slices: int) -> str:
        return OPTIONAL_SLICES_USER_STATUS_NORMAL_MESSAGE_TEMPLATE.format(slices=optional_slices)

    @staticmethod
    def status_user_summary(summary: OrderSummary) -> str:
        additional_info = [
            ("reg", summary.registered),
            ("opt", summary.optional),
            ("rem", summary.to_remove)
        ]
        additional_info_str = ", ".join(["%s=%d" % info for info in additional_info if info[1]])
        message = "{user_name} ({user_id}) - {slices}".format(
            user_name=summary.user_name,
            user_id=summary.user_id,
            slices=summary.order
        )

        return message if not additional_info else message + " (%s)" % additional_info_str

    @staticmethod
    def status(organizer: Organizer, pizzas: int, missing_slices: int, summaries: List[str]) -> str:
        return STATUS_MESSAGE_TEMPLATE.format(
            user_name=organizer.user_name,
            user_id=organizer.user_id,
            number_of_pizzas=pizzas,
            missing_slices=missing_slices,
            orders_summaries="\n".join(summaries) if len(summaries) else WHATEVER_MESSAGE,
        )

    @staticmethod
    def order(order: Order, slices: int) -> str:
        return ORDER_MESSAGE_TEMPLATE.format(
            user_name=order.user_name,
            user_id=order.user_id,
            slices=slices
        )

    @staticmethod
    def order_reduced(slices: int) -> str:
        return ORDER_REDUCED_MESSAGE_TEMPLATE.format(
            slices=slices
        )

    @staticmethod
    def order_removed() -> str:
        return ORDER_REMOVED_MESSAGE

    @staticmethod
    def error_not_started() -> str:
        return ERROR_NOT_STARTED

    @staticmethod
    def error_only_one_pizza() -> str:
        return ERROR_ONLY_ONE_PIZZA

    @staticmethod
    def error_only_owner_can_stop() -> str:
        return ERROR_ONLY_OWNER_CAN_STOP
