import os
import logging
from skpy import SkypeAuthException
from tinydb import TinyDB

from Core.PluginsLoader import PluginsLoader
from Core.SkypeClient import SkypeClient

logging.basicConfig(
    format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    username = os.environ.get('SKYPE_BOT_USERNAME', None)
    password = os.environ.get('SKYPE_BOT_PASSWORD', None)
    token_file = os.environ.get('SKYPE_BOT_TOKEN_FILE', os.path.join(os.getcwd(), 'token.txt'))
    database_file = os.environ.get('SKYPE_BOT_DATABASE_FILE', os.path.join(os.getcwd(), 'db.json'))

    if username is None or password is None or token_file is None:
        logger.critical('You must define following environment variables: SKYPE_BOT_USERNAME, SKYPE_BOT_PASSWORD')
        exit(-1)

    while True:
        try:
            plugins_types = PluginsLoader.load()
            logger.info("%d plugins loaded", len(plugins_types))
            database = TinyDB(database_file)
            logger.info("Database initialized at path %s", database_file)
            skype = SkypeClient(username=username, password=password, token_file=token_file)
            logger.info("SkypeClient initialized")
            plugins = [plugin(skype, database) for plugin in plugins_types]
            logger.info("Plugins initialized")
            skype.register_plugins(plugins)
            logger.info("Plugins registered")
            skype.setPresence()
            logger.info("SkypeBot started")
            skype.loop()
        except SkypeAuthException as ex:
            logger.exception("SkypeAuthException raised", ex)
        except Exception as ex:
            logger.critical("Unknown exception raised", ex)
            break
