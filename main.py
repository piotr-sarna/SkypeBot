import os
import logging
from skpy import SkypeAuthException

from Core.PluginsLoader import PluginsLoader
from Core.SkypeListener import SkypeListener

logging.basicConfig(
    format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

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
            logger.info("SkypeBot started")
            skype.loop()
        except SkypeAuthException as _:
            logger.exception("SkypeAuthException raised")
        except Exception as _:
            logger.exception("Unknown exception raised")
