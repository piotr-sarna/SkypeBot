import os
from Core.SkypeListener import SkypeListener


if __name__ == '__main__':
    username = os.environ.get('SKYPE_BOT_USERNAME', None)
    password = os.environ.get('SKYPE_BOT_PASSWORD', None)

    if username is None or password is None:
        print 'You must define following environment variables: SKYPE_BOT_USERNAME and SKYPE_BOT_PASSWORD'
        exit(-1)

    ping = SkypeListener(username=username, password=password)

    ping.loop()