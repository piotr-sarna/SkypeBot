import os
import logging
from typing import List

from skpy import SkypeAuthException
from tinydb import TinyDB

from Core.PluginBase import PluginBase
from Core.PluginsLoader import PluginsLoader
from Core.SkypeClient import SkypeClient

logging.basicConfig(
    format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def init_database() -> TinyDB:
    logger.debug("Initializing TinyDB...")
    db = TinyDB(database_file)
    logger.info("TinyDB initialized at path %s", database_file)
    return db


def init_client() -> SkypeClient:
    logger.debug("Initializing SkypeClient...")
    client = SkypeClient(username=username, password=password, token_file=token_file)
    logger.info("SkypeClient initialized for user %s", username)
    return client


def init_plugins(client: SkypeClient, database: TinyDB) -> List[PluginBase]:
    logger.debug("Detecting available plugins...")
    plugins_types = PluginsLoader.load()
    logger.debug("%d plugins detected", len(plugins_types))
    logger.debug("Initializing plugins...")
    plugins = [plugin(client, database) for plugin in plugins_types]
    plugins_names = ', '.join(list(map(lambda plugin: ("'%s'" % plugin.friendly_name()), plugins)))
    logger.info("Plugins initialized: %s", plugins_names)
    return plugins


def register_plugins(plugins: List[PluginBase], client: SkypeClient):
    logger.debug("Registering plugins at client...")
    client.register_plugins(plugins)
    logger.info("Plugins registered")


def run():
    database = init_database()
    client = init_client()
    plugins = init_plugins(client=client, database=database)
    register_plugins(plugins=plugins, client=client)

    while True:
        try:
            logger.debug("Setting presence...")
            client.setPresence()
            logger.info("SkypeBot started")
            client.loop()
        except SkypeAuthException as ex:
            logger.exception("SkypeAuthException raised", ex)
        except Exception as ex:
            logger.critical("Unknown exception raised", ex)
            break


if __name__ == '__main__':
    username = os.environ.get('SKYPE_BOT_USERNAME', None)
    password = os.environ.get('SKYPE_BOT_PASSWORD', None)
    token_file = os.environ.get('SKYPE_BOT_TOKEN_FILE', os.path.join(os.getcwd(), 'token.txt'))
    database_file = os.environ.get('SKYPE_BOT_DATABASE_FILE', os.path.join(os.getcwd(), 'db.json'))

    if username is None or password is None or token_file is None:
        logger.critical('You must define following environment variables: SKYPE_BOT_USERNAME, SKYPE_BOT_PASSWORD')
        exit(-1)

    run()
