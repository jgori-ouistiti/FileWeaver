import gi

gi.require_version("Nautilus", "3.0")
from gi.repository import Nautilus, GObject

from fileweaver.read_write import readwrite
from fileweaver.base import graph

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_FILES = config.get("FW-paths", "PATH_TO_FILES")
GFC_FORMATS = config.get("FW-values", "GFC_FORMATS")


import stat
import shutil
import subprocess
import itertools
import glob

import logging

logger = logging.getLogger(__name__)

from urllib.parse import unquote


class FlexFile:
    """Class made to make calls to a file easy (can be either via absolute path, vertex_index, linkname, of File Object).

    Call _get() to return:
        filename, linkname, cookbookpage, cookbookleftpage
	filename : absolute path before fw
	linkname : 'idfile_idpartition'
	cookbookpage : /.cookbook/linkname
	cookbookleftpage : cookbookleftpage/filename
    """

    def __init__(self, *args):
        if "NautilusVFSFile" in str(type(args[0])):
            filename, linkname, cookbookpage, cookbookleftpage = f_to_cbp(args[0])
            self.filename = filename
            self.linkname = linkname
            self.cookbookpage = cookbookpage
            self.cookbookleftpage = cookbookleftpage
        elif type(args[0]) == int:
            g, namemap = graph.open_graph()
            self.filename = g.vp.smlk[args[0]]
            self.cookbookleftpage = g.vp.path[args[0]]
            self.cookbookpage = os.path.dirname(self.cookbookleftpage)
            self.linkname = self.cookbookpage.split("/")[-1]
        elif type(args[0]) == str:
            # ==== Replacement
            path = os.path.abspath(args[0])
            try:
                linkname = path
                g, namemap = graph.open_graph()
                self.__init__(namemap[linkname])
            except KeyError:
                filename, linkname, cookbookpage, cookbookleftpage = fn_to_cbp(args[0])
                self.filename = filename
                self.linkname = linkname
                self.cookbookpage = cookbookpage
                self.cookbookleftpage = cookbookleftpage
            # ==== Replacement

            # if os.path.isabs(args[0]):
            #     filename, linkname, cookbookpage, cookbookleftpage = fn_to_cbp(args[0])
            #     self.filename = filename
            #     self.linkname = linkname
            #     self.cookbookpage = cookbookpage
            #     self.cookbookleftpage = cookbookleftpage
            # else:
            #     linkname = args[0]
            #     g, namemap = graph.open_graph()
            #     self.__init__(namemap[linkname])
        self.params = {}
        self.params["cluster"] = ""

    def _get(self):
        return self.filename, self.linkname, self.cookbookpage, self.cookbookleftpage

    def get_params(self):
        return self.params

    def update_param(self, key, value):
        self.params[key] = value

def fn_to_cbp(filename):
    linkname = generate_linkname(filename)
    cookbookpage = "/".join([PATH_TO_FILES, linkname])
    cookbookleftpage = "/".join([cookbookpage, os.path.basename(filename)])
    if "_v" in cookbookleftpage:
        # cookbookleftpage = "".join(cookbookleftpage.split("_v"))
        logging.debug("Calling a copy")
    return filename, linkname, cookbookpage, cookbookleftpage


def f_to_cbp(file):
    filename = get_filename(file)
    if filename == -1:
        logger.error("Problem with acquiring Filename")
        exit()
    return fn_to_cbp(filename)


def get_default_recipe(filename):
    """Gets default recipe

    Calls readwrite.read_default() and handles calls to other fields

    Args:
        filename (str): The absolute path to the file

    Returns:
        recipe (list): list of bash instructions

    """
    recipe = readwrite.read_default(filename, "recipe")
    if recipe[0] == "trace":
        return get_default_trace(filename)
    elif recipe[0] == "interact":
        return get_default_interact(filename)
    else:
        return recipe


def get_default_trace(filename):
    """Gets default trace

    Calls readwrite.read_default() and handles calls to other fields

    Args:
        filename (str): The absolute path to the file

    Returns:
        trace (list): list of bash instructions
    """
    trace = readwrite.read_default(filename, "trace")
    if trace[0] == "recipe":
        return get_default_recipe(filename)
    elif trace[0] == "interact":
        return get_default_interact(filename)
    else:
        return trace


def get_default_interact(filename):
    """Gets default interact

    Calls readwrite.read_default() and handles calls to other fields

    Args:
        filename (str): The absolute path to the file

    Returns:
        interact (list): list of bash instructions
    """
    interact = readwrite.read_default(filename, "interact")
    if interact[0] == "recipe":
        return get_default_recipe(filename)
    elif interact[0] == "trace":
        return get_default_trace(linkname)
    else:
        return interact


def get_default_format_img(filename):
    """Gets default format for images

    Calls readwrite.read_default()
    Args:
        filename (str): The absolute path to the file

    Returns:
        format (str):  '/'-separated formats in order of preference.
    """
    extension = filename.split(".")[-1]
    formatimg = readwrite.read_default(filename, "format-img")[0]
    return formatimg


def uses_morph(file):
    """Finds out if the file uses morphs.

    Tries to read usesmoprh flag, otherwise searches the file for generic formats

    Args:
        filename (str): The absolute path to the file

    Returns:
        uses_morph_flag (int):  flag value
    """
    filename, linkname, cookbookpage, cookbookleftpage = FlexFile(file)._get()
    if os.path.exists(cookbookpage):
        g, namemap = graph.open_graph()
        v = namemap.get(linkname)
        return g.vp.flags[3]
    else:
        with open(filename, "r") as fd:
            try:
                for line in fd:
                    if ".gifc" in line:
                        return 1
            except UnicodeDecodeError:
                pass
    return -1


def update_flags(linkname, diff):
    """Update usesmorph flag

    Reads the diff to find out the new value of the uses_morph flag
    Args:
        linkname (str):Linkname of  the file
        diff (list): an output of filedescriptor.readlines() or similar

    Returns:
        None
    """
    diffplus = []
    diffmin = []
    for nline, line in enumerate(diff):
        if nline < 3:
            pass
        else:
            if line[0] == "+":
                diffplus += [line]
            elif line[0] == "-":
                diffmin += [line]

    diffplus = "".join(diffplus)
    diffmin = "".join(diffmin)

    for gf in GFC_FORMATS:
        if ("." + gf) in diffplus:
            graph.update("vertex", "flags", linkname, 1, property_index=3)
            return

        if ("." + gf) in diffmin:
            g, namemap = graph.open_graph()
            condition = uses_morph(linkname)
            graph.close_graph(g, namemap)

            if condition == 1:
                graph.update("vertex", "flags", linkname, 1, property_index=3)
            else:
                graph.update("vertex", "flags", linkname, 0, property_index=3)
            return
    logging.debug("Flags not updated")
    return


def count_links(files):
    """Return the list of linked files from selection files

    Args:
        files (list): list of filenames that work with FlexFile()

    Returns:
        _linked (list): list of linked filenames
    """

    g, namemap = graph.open_graph()
    _linked = []
    for file in files:
        filename, linkname, cookbookpage, cookbookleftpage = FlexFile(file)._get()
        v = namemap.get(linkname)
        if v:
            _linked += [filename]
    return _linked


def get_filename(file):
    """Tries to get absolute path of the file.

    If the argument is a FileObject, gets filename using FileObject methods,
    otherwise checks if file is an absolute path.

    Args:
        file (str or FileObject): The absolute path to the file (str) or the FileObject file

    Returns:
        str: Returns the absolute path of the file if successful, or -1 if failed.

    """
    try:
        if file.get_uri_scheme() != "file":
            logger.error("Can't link folder for now")
            return -1
        filename = unquote(file.get_uri()[7:])
        return filename
    except AttributeError:
        if file.split(".")[-1] is not None and os.path.isabs(file):
            return file
        else:
            logger.error("Error: neither absolute path file nor folder")
            return -1
    return -1


def generate_linkname(filename):
    """Generate the linkname from the absolute path of the file.

    Args:
        filename (str): The absolute path to the file

    Returns:
        str: Returns the string {devicenumber}_{inodenumber}

    """
    stats = os.stat(filename)
    inn = stats[stat.ST_INO]
    dev = stats[stat.ST_DEV]
    return str(dev) + "_" + str(inn)
