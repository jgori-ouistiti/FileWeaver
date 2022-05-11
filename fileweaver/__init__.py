import os
import configparser

config = configparser.RawConfigParser()
config.read("conf.cfg")

PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")
PATH_TO_LINKS = config.get("FW-paths", "PATH_TO_LINKS")

os.environ["CONFIG_FILE"] = os.path.abspath(PATH_TO_LIBS + "/conf.cfg")


os.makedirs(PATH_TO_LINKS, exist_ok=True)


from .base import cooking
from .base import graph
from .base import linking
from .base import managing

from .read_write import readwrite
from .read_write import map_incoming_messages
