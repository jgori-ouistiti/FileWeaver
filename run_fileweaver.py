import os, subprocess
import configparser

config = configparser.RawConfigParser()
config.read("conf.cfg")

PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")

os.environ["CONFIG_FILE"] = os.path.abspath(PATH_TO_LIBS + "/conf.cfg")


newpid = os.fork()
if newpid == 0:
    # in child
    subprocess.run(
        f"python3 {PATH_TO_LIBS}fileweaver/scripts/fw_nautilus.py".split(" ")
    )
else:
    newpid = os.fork()
    if newpid == 0:
        subprocess.run(
            f"python3 {PATH_TO_LIBS}fileweaver/read_write/fw_server.py".split(" ")
        )
    else:
        pass
