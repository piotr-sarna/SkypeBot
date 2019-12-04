import os
from datetime import datetime
from Core.PluginsLoader import PluginsLoader
from Core.SkypeListener import SkypeListener

if __name__ == '__main__':
    username = os.environ.get('SKYPE_BOT_USERNAME', None)
    password = os.environ.get('SKYPE_BOT_PASSWORD', None)
    token_file = os.environ.get('SKYPE_BOT_TOKEN_FILE', os.path.join(os.getcwd(), 'token.txt'))

    if username is None or password is None or token_file is None:
        print('You must define following environment variables: SKYPE_BOT_USERNAME, SKYPE_BOT_PASSWORD')
        exit(-1)

    plugins = PluginsLoader().load()

    while True:
        try:
            skype = SkypeListener(username=username, password=password, token_file=token_file, plugins=plugins)

            skype.setPresence()
            print("SkypeBot started at " + str(datetime.now()))
            skype.loop()
        except Exception as e:
            print("Exception raised at" + str(datetime.now()))
            print(e)
