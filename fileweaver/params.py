
PATH_TO_LIBS = "/home/juliengori/Documents/VC/FileWeaver/fileweaver"
import gi

gi.require_version("Nautilus", "3.0")
import os

default_location_linking_system = os.environ["HOME"]
import shutil

PATH_TO_LINKS = "/".join([default_location_linking_system, ".cookbook/"])
PATH_TO_KITCHEN = PATH_TO_LIBS + "/default-kitchen"
PATH_TO_FILES = PATH_TO_LINKS + "files"
PATH_TO_DUMP = PATH_TO_LINKS + ".dump/"
PATH_TO_GRAPH = PATH_TO_LINKS + "graph.graphml"
PATH_TO_NAMEMAP = PATH_TO_LINKS + "namemap.pickle"
PATH_TO_LOG = PATH_TO_LINKS + "cookanum.log"
PATH_TO_INTERACTIVE_LOG = PATH_TO_LINKS + "interactive.log"
PATH_TO_TKDIFF = PATH_TO_KITCHEN + "/tkdiff"
PATH_TO_FW_PARTITION = "/home/juliengori/Documents/FileWeaver_Partition"


def startup():
    ### Managing folders
    for path in [PATH_TO_LINKS, PATH_TO_FILES, PATH_TO_DUMP]:
        try:
            shutil.rmtree(path)
        except OSError:
            pass
        try:
            os.mkdir(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))

    # ### Manage graph
    # try:
    #     os.remove(PATH_TO_GRAPH)
    # except OSError as e:
    #     print("Error: %s : %s" % (PATH_TO_GRAPH, e.strerror))
    #
    # try:
    #     os.remove(PATH_TO_NAMEMAP)
    # except OSError as e:
    #     print("Error: %s : %s" % (PATH_TO_NAMEMAP, e.strerror))


VERSION_NUMBER = ["A", "B", "C", "D", "E", "G", "H", "I", "J", "K", "L"]


IMG_FORMATS = ["jpg", "jpeg", "svg", "tiff", "gif", "png", "pdf"]
VID_FORMATS = ["mp4", "mpeg", "mkv", "avi"]


GFC_FORMATS = ["gifc"]
