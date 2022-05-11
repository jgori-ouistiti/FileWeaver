import configparser
import os, subprocess, shutil

config = configparser.RawConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")
PATH_TO_SHARED_FILE = config.get("Main", "PATH_TO_SHARED_FILE")
PATH_TO_JSON_SHARED_FILE = config.get("Main", "PATH_TO_JSON_SHARED_FILE")
PATH_TO_HIDDEN_JSON_SHARED_FILE = config.get("Main", "PATH_TO_HIDDEN_JSON_SHARED_FILE")

PATH_TO_LINKS = config.get("FW-paths", "PATH_TO_LINKS")
PATH_TO_FILES = config.get("FW-paths", "PATH_TO_FILES")
PATH_TO_DUMP = config.get("FW-paths", "PATH_TO_DUMP")
PATH_TO_SCRIPTS = config.get("FW-paths", "PATH_TO_SCRIPTS")


def startup():
    ### remove data from previous run
    for path in [PATH_TO_LINKS, PATH_TO_FILES, PATH_TO_DUMP]:
        try:
            shutil.rmtree(path)
        except OSError:
            pass
        try:
            os.mkdir(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))


shutil.move(f"{PATH_TO_LIBS}/fileweaver/scripts/linked_menu.py", f"{os.environ['HOME']}/.local/share/nautilus-python/extensions/")

startup()

from fileweaver.base import graph

import subprocess

##### Clean up stuff for demo
cmd = os.path.join(os.getcwd(), f"{PATH_TO_SCRIPTS}/startup_scenario_one.sh")
subprocess.call(cmd)
## Start an emptygraph
graph.init_graph()
## Make sure the shared file exists
with open(PATH_TO_SHARED_FILE, "w") as fd:
    fd.write("")
with open(PATH_TO_JSON_SHARED_FILE, "w") as fd:
    fd.write("")
with open(PATH_TO_HIDDEN_JSON_SHARED_FILE, "w") as fd:
    fd.write("")


print("Opening Nautilus")
subprocess.call("nautilus -q; nautilus", shell=True)
