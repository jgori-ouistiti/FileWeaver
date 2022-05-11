import os
import configparser

config = configparser.RawConfigParser()
config.read("conf.cfg")

PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")

os.environ["CONFIG_FILE"] = os.path.abspath(PATH_TO_LIBS + "/conf.cfg")

from .base import cooking
from .base import graph
from .base import linking
from .base import managing

from .read_write import readwrite
from .read_write import map_incoming_messages

