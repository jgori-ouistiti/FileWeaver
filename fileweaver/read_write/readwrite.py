import gi

gi.require_version("Nautilus", "3.0")
import subprocess
import time
import os
from datetime import datetime
import multiprocessing
import pickle
import time
import json


import sys


import configparser
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

config = configparser.RawConfigParser()
config.read(os.environ["CONFIG_FILE"])
PATH_TO_SHARED_FILE = config.get("Main", "PATH_TO_SHARED_FILE")
PATH_TO_JSON_SHARED_FILE = config.get("Main", "PATH_TO_JSON_SHARED_FILE")
PATH_TO_HIDDEN_JSON_SHARED_FILE = config.get("Main", "PATH_TO_HIDDEN_JSON_SHARED_FILE")


PATH_TO_KITCHEN = config["FW-paths"]["PATH_TO_KITCHEN"]

URI = "ws://localhost:8765"
pipe = "/home/juliengori/Documents/VC/FileWeaver/readwrite_server_pipe"


import logging

logger = logging.getLogger(__name__)


def read_default(filename, field):
    """Read a field from the default recipe.

    Args:
        filename (str): filename of the file that is being cooked.
        field (str): one of: "recipe", "trace", "interact", "format-img"
    Returns:
        out(list): content of the field (list of strings)


    """
    _extension = filename.split(".")[-1]
    if field == "recipe":
        delim_start = "=DEFAULT-RECIPE"
        delim_end = "!=DEFAULT-RECIPE"
    elif field == "trace":
        delim_start = "=DEFAULT-TRACE"
        delim_end = "!=DEFAULT-TRACE"
    elif field == "interact":
        delim_start = "=DEFAULT-INTERACT"
        delim_end = "!=DEFAULT-INTERACT"
    elif field == "format-img":
        delim_start = "=DEFAULT-FORMAT-IMG"
        delim_end = "!DEFAULT-FORMAT-IMG"
    with open("/".join([PATH_TO_KITCHEN, ".".join([_extension, "rcp"])]), "r") as fd:
        FLAG = 0
        out = []
        for nlines, line in enumerate(fd):
            line = line.rstrip("\n")
            if line == delim_end:
                FLAG = 0
            if FLAG == 1:
                out.append(line)
            if line == delim_start:
                FLAG = 1
        return out


### A simple lock to protect write actions. Write both a txt and a JSON file, with some differences in the syntax (see )
def write_to_shared_file(_str, out_json):
    lock = multiprocessing.Lock()
    lock.acquire()
    with open(PATH_TO_SHARED_FILE, "a") as fd:
        fd.write(_str)
    with open(PATH_TO_JSON_SHARED_FILE, "a") as fd:
        json.dump(out_json, fd, indent=1)
    with open(PATH_TO_HIDDEN_JSON_SHARED_FILE, "a") as fd:
        json.dump(out_json, fd, indent=1)
    lock.release()
    return


### Format vertex and edges properties to have the syntax: @VP <vertex_property_name> => <vertex_property_value>@, idem with EP.
def send_action(_str, vdic, edic):
    if vdic is not None:
        for key, value in vdic.items():
            if isinstance(value, list) and (isinstance(value[0], (int, float, bool))):
                value = "[" + ",".join([str(v) for v in value]) + "]"
            if isinstance(value, str):
                value.replace(" ", "")  #### Strip whitespace for lists
            _str = "@".join([_str, "VP {} => {} ".format(key, value)])
    if edic is not None:
        for key, value in edic.items():
            if not isinstance(value, (dict, list, tuple, int, float, str, bool)):
                value = str(value)
            if isinstance(value, list) and (isinstance(value[0], (int, float, bool))):
                value = "[" + ",".join([str(v) for v in value]) + "]"
            if isinstance(value, str):
                value.replace(" ", "")  #### Strip whitespace for lists
            _str = "@".join([_str, "EP {} => {} ".format(key, value)])
    return _str


### Translate the previous syntax to get dictionnaries back
def read_action(fields):
    vdic = {}
    edic = {}
    for field in fields:
        field = field.split(" ")
        if field[0] == "VP":
            if field[2] != "=>":
                print(
                    "the message passed has wrong syntax: {} should be an =>".format(
                        field[2]
                    )
                )
                return -2
            vdic[field[1]] = field[3]
        if field[0] == "EP":
            if field[2] != "=>":
                print(
                    "the message passed has wrong syntax: {} should be an =>".format(
                        field[2]
                    )
                )
                return -2
            edic[field[1]] = field[3]
    return vdic, edic


#### Here we define a mini language to facilitate communication of the graph between apps.
# The rule is a follows. Each line starts with  G if the instructions are incremental graph building instructions, V if they are graph view instructions.
# Separator for each field is @. Any number of VP and EP can be added.
def send_instruction_over(linkname, action, id, vdic=None, edic=None):
    # Syntax is "G@id@Action@V#=>Value@VP#=>Value@...@EP#=>Value@..."

    # Current Action set:
    #   - Add
    #   - Add edge
    #   - Update

    out_str = "@".join(["G", linkname, action, str(id)])
    out_str = send_action(out_str, vdic, edic)
    out_json = {}
    out_json["type"] = "G"
    out_json["linkname"] = linkname
    out_json["action"] = action
    out_json["id"] = str(id)
    out_json["vpdic"] = vdic
    out_json["epdic"] = edic
    print("json")
    print(out_json)
    # ws = websocket.WebSocket()
    # ws.connect(URI)
    # ws.send(json.dumps(out_json))
    # ws.close()
    msg = json.dumps(out_json)
    print(f"sending: {msg} ({type(msg)})")
    socket.send_string(msg)
    # msg = socket.recv()
    # print("=============================================== DONE WRITING")
    # print(f"received  {msg}")
    return write_to_shared_file(out_str + "\n", out_json)


def send_view_over(linknames):
    # Syntax is "V@linkname_1,linkname2,..."
    if linknames:
        out_str = "@".join(["V", ",".join(linknames)])
        out_json = {}
        out_json["type"] = "V"
        out_json["linkname"] = linknames
        return write_to_shared_file(out_str + "\n", out_json)
    else:
        pass


### Read from shared file and decode the message into the needed data structures
def get_instruction():
    out = []
    list_str = read_from_shared_file()
    for _str in list_str:
        if _str == "null":
            pass
        else:
            fields = _str.split("@")
            _check = fields.pop(0)
            if _check == "G":
                linkname = fields.pop(0)
                action = fields.pop(0)
                id = fields.pop(0)
                vdic, edic = read_action(fields)
                out.append(("G", id, action, vdic, edic))
            elif _check == "V":
                linknames = fields.pop(0)
                out.append(("V", linknames))
    return out


### Actually read from file. A simple lock protects this.
### Important: after reading, the file is flushed (content erased)
def read_from_shared_file():
    lock = multiprocessing.Lock()
    lock.acquire()
    with open(PATH_TO_SHARED_FILE, "r") as fd:
        _str = fd.readlines()
    with open(PATH_TO_SHARED_FILE, "w") as fd:
        fd.writelines([""])
    lock.release()
    return _str
