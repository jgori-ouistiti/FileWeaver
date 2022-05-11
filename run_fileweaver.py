import os, subprocess
import configparser

config = configparser.RawConfigParser()
config.read("conf.cfg")

PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")

os.environ["CONFIG_FILE"] = os.path.abspath(PATH_TO_LIBS + "/conf.cfg")
os.environ["XDG_DATA_HOME"] = f"{os.environ['HOME']}/.local/share/"

PATH_TO_FW_PARTITION = config.get("FW-paths", "PATH_TO_FW_PARTITION")
os.makedirs(PATH_TO_FW_PARTITION, exist_ok = True)


subprocess.run("fuser -k 5555/tcp".split(" "))

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
