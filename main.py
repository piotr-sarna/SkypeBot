import logging
import os
from collections import namedtuple
from typing import List

from tinydb import TinyDB

from Core.PluginBase import PluginBase
from Core.PluginsLoader import PluginsLoader
from Core.SkypeClient import SkypeClient

logging.basicConfig(
    format='%(asctime)s %(module)s %(levelname)-8s %(message)s',
    level=os.environ.get('SKYPE_LOGGING_LEVEL', 'INFO'),
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

Environment = namedtuple("Environment", ["username", "password", "token_file", "database_file"])


def read_environment() -> Environment:
    logger.debug("Reading environment variables...")
    username = os.environ.get('SKYPE_BOT_USERNAME', None)
    password = os.environ.get('SKYPE_BOT_PASSWORD', None)
    token_file = os.environ.get('SKYPE_BOT_TOKEN_FILE', os.path.join(os.getcwd(), 'token.txt'))
    database_file = os.environ.get('SKYPE_BOT_DATABASE_FILE', os.path.join(os.getcwd(), 'db.json'))

    if username is None or password is None or token_file is None:
        logger.critical('You must define following environment variables: SKYPE_BOT_USERNAME, SKYPE_BOT_PASSWORD')
        exit(-1)

    logger.info("All required environment variables are set")
    return Environment(username, password, token_file, database_file)


def init_database(env: Environment) -> TinyDB:
    logger.debug("Initializing TinyDB...")
    db = TinyDB(env.database_file)
    logger.info("TinyDB initialized at path %s", env.database_file)
    return db


def init_client(env: Environment) -> SkypeClient:
    logger.debug("Initializing SkypeClient...")
    client = SkypeClient(username=env.username, password=env.password, token_file=env.token_file)
    logger.info("SkypeClient initialized for user %s", env.username)
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
    env = read_environment()
    database = init_database(env)
    client = init_client(env)
    plugins = init_plugins(client=client, database=database)
    register_plugins(plugins=plugins, client=client)

    logger.debug("Setting presence...")
    client.setPresence()
    logger.info("SkypeBot started")
    client.loop()


if __name__ == '__main__':
    run()
