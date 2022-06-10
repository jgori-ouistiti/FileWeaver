import os, subprocess
import configparser

config = configparser.ConfigParser()
config.read("conf.ini")

path_to_lib = os.path.abspath(config["Library"]["PATH_TO_LIBS"])
fw_partition = os.path.abspath(config["FileWeaver_Partition"]["FW_PARTITION"])
default_location_linking_system = os.environ["HOME"]


PATH_TO_LIBS = f"{path_to_lib}/"
PATH_TO_SHARED_FILE = f"{path_to_lib}/.exchange.txt"
PATH_TO_JSON_SHARED_FILE = f"{path_to_lib}/exchange.json"
PATH_TO_HIDDEN_JSON_SHARED_FILE = f"{path_to_lib}/.exchange.json"

PATH_TO_LINKS = f"{default_location_linking_system}/.cookbook"
PATH_TO_KITCHEN = f"{path_to_lib}/fileweaver/default-kitchen/"
PATH_TO_FILES = f"{PATH_TO_LINKS}/files/"
PATH_TO_DUMP = f"{PATH_TO_LINKS}/.dump/"
PATH_TO_SCRIPTS = f"{path_to_lib}/scripts"
PATH_TO_GRAPH = f"{PATH_TO_LINKS}/graph.graphml"
PATH_TO_NAMEMAP = f"{PATH_TO_LINKS}/namemap.pickle"
PATH_TO_LOG = f"{PATH_TO_LINKS}/cookanum.log"
PATH_TO_TKDIFF = f"{path_to_lib}/fileweaver/default-kitchen/tkdiff"
PATH_TO_INTERACTIVE_LOG = f"{PATH_TO_LINKS}/interactive.log"
PATH_TO_FW_PARTITION = fw_partition

VERSION_NUMBER = ["A", "B", "C", "D", "E", "G", "H", "I", "J", "K", "L"]
IMG_FORMATS = ["jpg", "jpeg", "svg", "tiff", "gif", "png", "pdf"]
VID_FORMATS = ["mp4", "mpeg", "mkv", "avi"]
GFC_FORMATS = ["gifc"]


def write_conf_file():
    with open("conf.cfg", "w") as fd:
        fd.write("[Main]")
        fd.write("\n")
        fd.write(f"PATH_TO_LIBS = {PATH_TO_LIBS}")
        fd.write("\n")
        fd.write(f"PATH_TO_SHARED_FILE = {PATH_TO_SHARED_FILE}")
        fd.write("\n")
        fd.write(f"PATH_TO_JSON_SHARED_FILE = {PATH_TO_JSON_SHARED_FILE}")
        fd.write("\n")
        fd.write(f"PATH_TO_HIDDEN_JSON_SHARED_FILE = {PATH_TO_HIDDEN_JSON_SHARED_FILE}")
        fd.write("\n")
        fd.write("\n")
        fd.write("[FW-paths]")
        fd.write("\n")
        fd.write(f"PATH_TO_LINKS = {PATH_TO_LINKS}")
        fd.write("\n")
        fd.write(f"PATH_TO_KITCHEN = {PATH_TO_KITCHEN}")
        fd.write("\n")
        fd.write(f"PATH_TO_FILES = {PATH_TO_FILES}")
        fd.write("\n")
        fd.write(f"PATH_TO_DUMP = {PATH_TO_DUMP}")
        fd.write("\n")
        fd.write(f"PATH_TO_SCRIPTS = {PATH_TO_SCRIPTS}")
        fd.write("\n")
        fd.write(f"PATH_TO_GRAPH = {PATH_TO_GRAPH}")
        fd.write("\n")
        fd.write(f"PATH_TO_NAMEMAP = {PATH_TO_NAMEMAP}")
        fd.write("\n")
        fd.write(f"PATH_TO_LOG = {PATH_TO_LOG}")
        fd.write("\n")
        fd.write(f"PATH_TO_TKDIFF = PATH_TO_TKDIFF")
        fd.write("\n")
        fd.write(f"PATH_TO_INTERACTIVE_LOG = {PATH_TO_INTERACTIVE_LOG}")
        fd.write("\n")
        fd.write(f"PATH_TO_FW_PARTITION = {PATH_TO_FW_PARTITION}")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("[FW-values]")
        fd.write("\n")
        fd.write(f"VERSION_NUMBER = {VERSION_NUMBER}")
        fd.write("\n")
        fd.write(f"IMG_FORMATS = {IMG_FORMATS}")
        fd.write("\n")
        fd.write(f"VID_FORMATS = {VID_FORMATS}")
        fd.write("\n")
        fd.write(f"GFC_FORMATS = {GFC_FORMATS}")
        fd.write("\n")


def scenario_one():
    with open(os.path.join(PATH_TO_LIBS, "scenarios", "scenario_one", "scnr.sh"), "w") as fd:
        fd.write("#!/bin/bash")
        fd.write("\n")
        fd.write(
            f"find {PATH_TO_FW_PARTITION} -maxdepth 1 -mindepth 1 -not -name 'scenario*' | xargs rm -rf"
        )
        fd.write("\n")
        fd.write(
            f"cp -r {PATH_TO_LIBS}/scenarios/scenario_one/files/* {PATH_TO_FW_PARTITION}/"
        )
        fd.write("\n")
        fd.write(f"chmod u+w {PATH_TO_FW_PARTITION}*.tex")
        fd.write("\n")
        fd.write(f"chmod u+w {PATH_TO_FW_PARTITION}*.py")
        fd.write("\n")


def scenario_two():
    with open(
        os.path.join(PATH_TO_LIBS, "scenarios", "scenario_two", "scnr.sh"), "w"
    ) as fd:
        fd.write("#!/bin/bash")
        fd.write("\n")
        fd.write(
            f"find {PATH_TO_FW_PARTITION} -maxdepth 1 -mindepth 1 -not -name 'scenario*' | xargs rm -rf"
        )
        fd.write("\n")
        fd.write(
            f"cp -r {PATH_TO_LIBS}/scenarios/scenario_two/files/* {PATH_TO_FW_PARTITION}/"
        )
        fd.write("\n")
        fd.write(f"chmod u+w {PATH_TO_FW_PARTITION}*.tex")
        fd.write("\n")
        fd.write(f"chmod u+w {PATH_TO_FW_PARTITION}*.py")
        fd.write("\n")


def startup_scenario_one():
    with open(
        os.path.join(PATH_TO_LIBS, "scripts", "startup_scenario_one.sh"), "w"
    ) as fd:
        fd.write("#!/bin/bash")
        fd.write("\n")
        fd.write(f"{PATH_TO_LIBS}/scenarios/scenario_one/scnr.sh")
        fd.write("\n")
        fd.write(f"rm -f {PATH_TO_GRAPH}")
        fd.write("\n")
        fd.write(f"rm -f {PATH_TO_NAMEMAP}")
        fd.write("\n")
        fd.write(f"rm -f {PATH_TO_HIDDEN_JSON_SHARED_FILE}")
        fd.write("\n")
        fd.write(f"rm -f {PATH_TO_JSON_SHARED_FILE}")
        fd.write("\n")

def startup_scenario_complex():
	with open(
		os.path.join(PATH_TO_LIBS, "scripts", "startup_scenario_complex.sh"), "w"
	) as fd:
		fd.write("#!/bin/bash")
		fd.write("\n")
		fd.write(f"rm -f {PATH_TO_GRAPH}")
		fd.write("\n")
		fd.write(f"rm -f {PATH_TO_NAMEMAP}")
		fd.write("\n")
		fd.write(f"rm -f {PATH_TO_HIDDEN_JSON_SHARED_FILE}")
		fd.write("\n")
		fd.write(f"rm -f {PATH_TO_JSON_SHARED_FILE}")
		fd.write("\n")
		fd.write(f"gh=\"https://github.com/AllenDowney/ThinkDSP\"")
		fd.write("\n")
		fd.write(f"git clone $gh {PATH_TO_FW_PARTITION}")
		

def write_scripts():
    scenario_one()
    scenario_two()
    startup_scenario_one()
    startup_scenario_complex()
    os.chmod(os.path.join(PATH_TO_LIBS, "scenarios", "scenario_one", "scnr.sh"), 0o777)
    os.chmod(os.path.join(PATH_TO_LIBS, "scenarios", "scenario_two", "scnr.sh"), 0o777)
    os.chmod(os.path.join(PATH_TO_LIBS, "scripts", "startup_scenario_one.sh"), 0o777)
    os.chmod(os.path.join(PATH_TO_LIBS, "scripts", "startup_scenario_complex.sh"), 0o777)


def stracegawk():
    try:
        subprocess.run(
            [
                "ln",
                "-s",
                os.path.join(PATH_TO_LIBS, "scripts/stracegawk"),
                f"{os.environ['HOME']}/.local/bin/",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        pass


if __name__ == "__main__":
    write_conf_file()
    write_scripts()
    stracegawk()				
