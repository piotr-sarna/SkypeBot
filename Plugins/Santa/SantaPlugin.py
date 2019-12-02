from skpy import SkypeNewMessageEvent, SkypeEditMessageEvent
from numpy import random

from Core.PluginBase import PluginBase
from .Command import Command


def check_if_correctly_shuffled(participants, draw_participants):

    for i in range(len(participants)):
        if participants[i] == draw_participants[i]:
            return False
    return True


class SantaPlugin(PluginBase):
    def __init__(self, skype):
        super(SantaPlugin, self).__init__(skype=skype)
        self._participants = {}
        self._started_by = None

    def friendly_name(self):
        return 'Santa plugin'

    def version(self):
        return '0.1'

    def keywords(self):
        return ['santa']

    def handle(self, event):
        if not isinstance(event, SkypeNewMessageEvent) and not isinstance(event, SkypeEditMessageEvent):
            return

        message = event.msg
        command = Command.parse(message=message.markup)

        if self._process_if_help_command(message=message, command=command):
            return

        if command.start:
            self._handle_start(message=message, command=command)
        elif command.stop:
            self._handle_stop(message=message, command=command)
        elif command.participate:
            self._handle_participate(message=message, command=command)
        elif command.status:
            self._handle_status(message=message, command=command)

    def help_message(self):
        return """{friendly_name} v{version}
           
Keywords: {keywords}
Commands:
    #help
    #start
    #bylemgrzeczny
    #stop
    #status
""".format(friendly_name=self.friendly_name(),
           version=self.version(),
           keywords=','.join(['#' + keyword for keyword in self.keywords()])
           )

    def _process_if_help_command(self, message, command):
        if command.help:
            self._skype.contacts[message.userId].chat.sendMsg(self.help_message())

        return command.help

    def _handle_start(self, message, command):
        if self._started_by:
            raise Exception("Aekhem, there's only one Santa! \n"
                            "Exactly one #santa can be started at the same time")

        self._started_by = message.user

        self._skype.contacts[message.user.id].chat.sendMsg(
            "You've started #santa {time} UTC. Please remember to #santa #stop".format(time=str(message.time.replace(
                microsecond=0)))
        )

        message.chat.sendMsg("#santa started by {user_name} ({user_id})".format(user_name=self._started_by.name,
                                                                                user_id=self._started_by.id))
        message.chat.sendMsg(self.help_message());

    def _handle_stop(self, message, command):
        if not self._started_by:
            raise Exception("No #santa is currently started")

        if self._started_by.id != message.userId:
            raise Exception("Only user who started #santa can stop it")

        total_participants = len(self._participants)
        participants_summary = ["{user_name} ({user_id})".format(user_name=self._participants[participant].name,
                                                                user_id=self._participants[participant].id)
                               for participant in self._participants]

        # start draw
        draw_participants = []

        for participant in self._participants:
            draw_participants.append(self._participants[participant].id)

        participants = draw_participants[:]

        random.shuffle(draw_participants)
        
        while not check_if_correctly_shuffled(participants, draw_participants):
            random.shuffle(draw_participants)

        draw_results = {}

        for i in range(len(participants)):
            draw_results[participants[i]] = draw_participants[i]

        self._skype.contacts[message.userId].chat.sendMsg(
            """You've stopped #santa at {time} UTC,

Summary:
Total participants: {total_participants}

Participants list:
{participants_list}
""".format(time=str(message.time.replace(microsecond=0)),
            total_participants=total_participants,
            participants_list="\n".join(participants_summary))
        )

        message.chat.sendMsg(
"""Summary:
Total participants: {total_participants}

Participants list:
{participants_list}
        """.format(time=str(message.time.replace(microsecond=0)),
                    total_participants=total_participants,
                    participants_list="\n".join(participants_summary))
        )

        for participant in draw_results:
            self._skype.contacts[participant].chat.sendMsg(
"""Your draw is: {user_name} ({user_id}).
""".format(time=str(message.time.replace(microsecond=0)),
            user_name=self._participants[draw_results[participant]].name,
            user_id=draw_results[participant])
            )

        self._participants = {}
        self._started_by = None

    def _handle_participate(self, message, command):
        if not self._started_by:
            raise Exception("No #santa is currently started")

        if message.userId in self._participants.keys():
            del self._participants[message.userId]

        if command.participate:
            self._participants[message.userId] = message.user

        self._skype.contacts[message.userId].chat.sendMsg("You're on #santa's list now!")

    def _handle_status(self, message, command):
        total_participants = len(self._participants)
        participants_summary = ["{user_name} ({user_id})".format(user_name=self._participants[participant].name,
                                                                user_id=self._participants[participant].id)
                               for participant in self._participants]

        message.chat.sendMsg(
"""Total participants now: {total_participants}.
Current participants list:
{participants_list}
""".format(time=str(message.time.replace(microsecond=0)),
            total_participants=total_participants,
            participants_list="\n".join(participants_summary))
        )
