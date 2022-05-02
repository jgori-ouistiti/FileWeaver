import gi

gi.require_version("Nautilus", "3.0")
from gi.repository import Nautilus, GObject


import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_FW_PARTITION = config.get("FW-paths", "PATH_TO_FW_PARTITION")
VERSION_NUMBER = config.get("FW-values", "VERSION_NUMBER")
PATH_TO_DUMP = config.get("FW-paths", "PATH_TO_DUMP")

from fileweaver.read_write import readwrite
from fileweaver.base import graph
from fileweaver.base import managing
from fileweaver.base import linking

from fileweaver.git_integration import nautgit
import graph_tool.topology as gtt


import numpy

import os
import shutil
import logging

logger = logging.getLogger(__name__)

import subprocess
import sys
import stat
import time
import random


@managing.exists_decorator
def edit_linked_file(file):
    """Edit a link.

    If the link does not exist then create it. Then track it using version control.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:


    """
    cookbookpage, linkname = (
        linking.FlexFile(file).cookbookpage,
        linking.FlexFile(file).linkname,
    )
    msg = nautgit.read_logmsg_repo(cookbookpage)
    logging.info("Link established, last entry was \t {}".format(msg))
    #### Atom makes this a non-blocking call. Sort this out later, but it is ok for now, since commit to repo is blocking
    run_interactive_mode(file)
    logger.info("Going to commit revision")
    diff = nautgit.commit_to_repo(cookbookpage)
    linking.update_flags(linkname, diff)
    logging.info(
        "I am now refreshing all nodes upstream of this one, this node included"
    )
    g, namemap = graph.open_graph()
    last_chain_link = refresh_file(file)
    run_interactive_mode(g.vp.smlk[last_chain_link])


def refresh_file(file):
    """Refresh a link.

    Finds all cakes and updates them.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        None

    """
    ##refresh links
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    (cakes, cflag), (deps, dflag) = check_link(file)
    print("checlkink output")
    print(cakes)

    logging.info("\n I found the following cakes | Update necessary : {}".format(cflag))
    logging.debug(cakes)
    logging.info("and deps | Update necessary: {}".format(dflag))
    logging.debug(deps)

    for d in deps:
        cookbookpage = managing.new_link(d, restore=False)

    if dflag:
        update_deps_in_graph(deps, file)
    g, namemap, subg = graph.get_subgraph_spawns(linkname)
    logging.debug("I am looking at this subgraph")
    _array = update_graph(subg)
    check_cakes(file, cakes)
    return _array[-1]


def update_graph(g):
    """update the node contents of the graph.

    Perform a topological sort and run recipe in that order on the graph g.  (All nodes will be updated, so use the right subgraph)

    Args:
        g (graph object): the graph that will be updated

    Returns:


    """
    try:
        _array = gtt.topological_sort(g)
    except ValueError:
        graph.draw_graph()
        _array = gtt.topological_sort(g)
    logging.debug("I am updating in the following order")
    logging.debug(_array)
    for v in _array:
        run_recipe(int(v))
    return _array


def run_interactive_mode(file):
    """Run the file in interactive mode.


    Args:
        cookbookpage (str): The page where to find the leftcookbookpage

    Returns:


    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    _script = generate_interact(linkname)
    logger.info("I am going to run script {}".format(_script))
    bash_cmd = ["bash", _script, filename]
    logger.info("Opening file {}".format(filename))
    subprocess.call(bash_cmd)
    logger.info("Finished working on file")
    return 0


def add_file_and_children(file):
    """Cook the file, i.e. apply its recipe.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:

    """

    logger.info("\n\n\nStarting to cook\n")
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    (cakes, cflag), (deps, dflag) = check_link(file)
    logging.info("\n I found the following cakes | Update necessary : {}".format(cflag))
    logging.debug(cakes)
    logging.info("and deps | Update necessary: {}".format(dflag))
    logging.debug(deps)

    ##### Here this calls the unmorphed files, which do not exist as symlink, creating an error
    for d in deps:
        cookbookpage = managing.new_link(d)
    if dflag:
        update_deps_in_graph(deps, file)
    add_dependency(file)
    run_recipe(file)
    check_cakes(file, cakes)
    return


def check_cakes(file, cakes):
    """Updates dependency list of cakes after cooking main meal.


    For each cake, determine if it should be kept or not. The current setting is to keep all files, except those that are not hidden in the home directory. Also deals with temporary files that are only used during building, under the heading: gluttonous chef ate the cake.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        None: Might add more informative returns


    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    keep_cakes = []
    for cake in cakes:
        KEEP_FLAG = 0
        if (not (os.environ["HOME"] + "/.") in cake) and (cake != filename):
            try:
                cake_cookbookpage = managing.new_link(cake)
                KEEP_FLAG = 1
            except OSError:
                logger.info(
                    "Cake {} was eaten by the gluttonous chef (it was likely a temporary file)".format(
                        cake
                    )
                )
        if KEEP_FLAG:
            keep_cakes.append(cake)
    update_cakes_in_graph(keep_cakes, file)
    return None


@managing.attach_link_decorator
def update_deps_in_graph(deps, file, send=True):
    """Updates dependency in graph.


    I think this line can return Error: g.ep.update_time[e] = time.time(), but can't seem to reproduce it for now.
    Makes edges between each (dep in deps) and file, update  update_time and edge_dir_up

    Args:
        deps (list): list of absolute paths to the deps that need to be added to file.
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        1 if successful


    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    g, namemap = graph.open_graph()

    in_edges = g.get_in_edges(namemap[linkname])
    if deps:
        for d in deps:
            cookbookpage_dep = managing.new_link(d)
            if cookbookpage_dep is None:
                continue

            linkname_dep = cookbookpage_dep.split("/")[-1]
            _edge = [namemap[linkname_dep], namemap[linkname]]
            flag_add = False
            rev_edge = [namemap[linkname], namemap[linkname_dep]]
            ### If an edge with reverse child-parent already exists, then do nothing (we have to preserve DAG structure of the graph; this should never occur though)
            if (rev_edge == in_edges).all(axis=1).any():
                continue
            ### If the edge is new:
            elif not (_edge == in_edges).all(axis=1).any():
                flag_add = True
                e = g.add_edge(*_edge)
                g.ep.update_bool[e] = 1
                if g.vp.flags[namemap[linkname_dep]][2] == 1:  # If the dep is a morph:
                    g.ep.format[e] = str(linking.get_default_format_img(filename))
            ### If the edge already exists:
            else:
                in_edges = in_edges[~(in_edges == [_edge[0], _edge[1]]).all(axis=1), :]
                e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
            _time = time.time()
            g.ep.update_time[e] = _time
            g.ep.edge_dir_up[e] = bool(0)
            vhash = g.vp.version[namemap[linkname_dep]]
            g.ep.parent_version[e] = vhash

            #### Send to interactive window
            if send is True:
                edic = {}
                if flag_add is True:
                    action = "add_edge"
                    edic["update_bool"] = bool(1)
                    edic["format"] = str(g.ep.format[e])
                else:
                    action = "update_edge"

                edic["update_time"] = _time
                edic["edge_dir_up"] = bool(0)
                edic["parent_version"] = vhash
                _id = "{}#{}".format(_edge[0], _edge[1])
                readwrite.send_instruction_over(linkname, action, _id, {}, edic)

        # Remove all edges that not longer exist
        for s, t in in_edges:
            g.remove_edge(g.edge(g.vertex(s), g.vertex(t)))
            _id = "{}#{}".format(s, t)
            readwrite.send_instruction_over(linkname, "delete_edge", _id)

    else:
        _time = time.time()
        graph.update("vertex", "emptyin", linkname, _time, g=g, namemap=namemap)
    graph.close_graph(g, namemap)

    return 1


@managing.attach_link_decorator
def update_cakes_in_graph(cakes, file, send=True):
    """Updates cakes in graph.


    I think this line can return Error: g.ep.update_time[e] = time.time(), but can't seem to reproduce it for now.
    Makes edges between each (cake in cakes) and file, update  update_time and edge_dir_up

    Args:
        deps (list): list of absolute paths to the deps that need to be added to file.
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        1 if successful


    """

    logging.debug("Entering update cakes")
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    g, namemap = graph.open_graph()
    print("out edges when entering update cakes")
    out_edges = g.get_out_edges(namemap[linkname])
    print(out_edges)
    remaining_out_edges = numpy.copy(out_edges)
    if cakes:
        for c in cakes:
            print("entering cake {}".format(c))
            cookbookpage_cake = managing.new_link(c, restore=False)
            if isinstance(
                cookbookpage_cake, str
            ):  ## If the link creation was successfull
                linkname_cake = cookbookpage_cake.split("/")[-1]
            else:
                continue

            _edge = [namemap[linkname], namemap[linkname_cake]]
            flag_add = False
            rev_edge = [namemap[linkname_cake], namemap[linkname]]
            ### If an edge with reverse child-parent already exists, then do nothing (we have to preserve DAG structure of the graph)
            if (rev_edge == out_edges).all(axis=1).any():
                continue

            ### If a new edge, add it
            elif not (_edge == out_edges).all(axis=1).any():
                flag_add = True
                e = g.add_edge(*_edge)
                g.ep.update_bool[e] = bool(1)
                if g.vp.flags[namemap[linkname_cake]][2] == 1:  # If the dep is a morph:
                    g.ep.format[e] = str(linking.get_default_format_img(filename))
            ### if edge already exists, update it
            else:
                e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
            print("here")
            print(remaining_out_edges)
            remaining_out_edges = remaining_out_edges[
                ~(remaining_out_edges == [_edge[0], _edge[1]]).all(axis=1), :
            ]
            _time = time.time()
            g.ep.update_time[e] = _time
            g.ep.edge_dir_up[e] = bool(0)

        print("new out_edges stuff")
        out_edges = g.get_out_edges(namemap[linkname])
        print(out_edges)
        print("old out edges that are not cakes anymore")
        print(remaining_out_edges)
        for s, t in out_edges:
            if not (remaining_out_edges == [s, t]).all(axis=1):
                e = g.edge(g.vertex(s), g.vertex(t))
                vhash = g.vp.version[namemap[linkname]]
                g.ep.parent_version[e] = vhash
            else:
                vhash = g.ep.parent_version[e]

            if send is True:
                edic = {}
                if flag_add is True:
                    action = "add_edge"
                    edic["update_bool"] = bool(1)
                    edic["format"] = str(g.ep.format[e])
                else:
                    action = "update_edge"

                edic["update_time"] = _time
                edic["edge_dir_up"] = bool(1)
                edic["parent_version"] = vhash
                _id = "{}#{}".format(_edge[0], _edge[1])
                readwrite.send_instruction_over(linkname, action, _id, {}, edic)

    else:
        _time = time.time()
        graph.update("vertex", "emptyout", linkname, _time, g=g, namemap=namemap)
    graph.close_graph(g, namemap)
    return 1


@managing.morph_decorator
def run_recipe(file):
    """Run recipe needed to cook the file.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        None: Might add more informative returns


    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    _script = generate_recipe(linkname)
    bash_cmd = ["bash", _script, filename]
    subprocess.call(bash_cmd)
    logger.info(
        "target {} cooked; enjoy your meal --- updating cakes".format(cookbookleftpage)
    )
    return None


def add_dependency(file):
    """Cook dependencies.


    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        None: Might add more informative returns


    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    g, namemap = graph.open_graph()

    dep_vertices = g.get_in_edges(namemap[linkname])[:, 0]
    for dep in dep_vertices:
        filename = g.vp.smlk[dep]
        add_file_and_children(filename)
    return None


@managing.exists_decorator
@managing.morph_decorator
def check_link(file, send=True):
    """Update the link for dependencies and cakes.

    Args:
        file (str/FileObject): The absolute path to the file or a FileObject

    Returns:
        cake (list): List of all cakes of the file
        dependencies (list): List of all dependencies of the file



    """

    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    FILE_ACCESS_TIME = os.stat(filename)[stat.ST_MTIME]

    g, namemap = graph.open_graph()
    v = namemap.get(linkname)
    if v is None:
        cakes_need_to_be_updated = True
        deps_need_to_be_updated = True
    else:
        edges = g.get_out_edges(v, eprops=[g.ep.update_time, g.ep.update_bool])
        if edges.any():
            if (
                numpy.min(numpy.ma.masked_array(edges[:, 2], ~edges[:, 3].astype(bool)))
                > FILE_ACCESS_TIME
            ):
                logging.info(
                    "Node had out edges brought up to date after last modif of file, no need to update cakes"
                )
                cakes_need_to_be_updated = False
            else:
                logging.info(
                    "Node had out edges brought up to date before last modif of file, need to update cakes"
                )
                cakes_need_to_be_updated = True
        else:
            if g.vp.emptyout[v] > FILE_ACCESS_TIME:
                logging.info("Node without out edges | No need to update")
                cakes_need_to_be_updated = False
            else:
                logging.info("Node without out edges | Need to update")
                cakes_need_to_be_updated = True

        edges = g.get_in_edges(v, eprops=[g.ep.update_time, g.ep.update_bool])
        if edges.any():
            if (
                numpy.min(numpy.ma.masked_array(edges[:, 2], ~edges[:, 3].astype(bool)))
                > FILE_ACCESS_TIME
            ):
                logging.info(
                    "Node had in edges brought up to date after last modif of file, no need to update deps"
                )
                deps_need_to_be_updated = False
            else:
                logging.info(
                    "Node had in edges brought up to date before last modif of file, need to update deps"
                )
                deps_need_to_be_updated = True
        else:
            if g.vp.emptyin[v] > FILE_ACCESS_TIME:
                logging.info("Node without in edges | No need to update")
                deps_need_to_be_updated = False
            else:
                logging.info("Node without in edges | Need to update")
                deps_need_to_be_updated = True

    if cakes_need_to_be_updated:
        logging.debug("I am updating cakes for {}".format(filename))
        print("I am updating cakes for {}".format(filename))
        cakes = get_cakes(file)
    else:
        logging.debug("I am simply reading off the cakes")
        cakes = read_cakes(g, namemap, linkname)

    print("\n=====")
    print(cakes)
    print("\n=======")

    if deps_need_to_be_updated:
        logging.debug("I am updating deps for {}".format(filename))
        deps = get_deps(file, cakes)
    else:
        logging.debug("I am simply reading off the deps")
        deps = read_deps(g, namemap, linkname)

    if cakes_need_to_be_updated:
        cakes = (cakes, 1)
    else:
        cakes = (cakes, 0)

    if deps_need_to_be_updated:
        deps = (deps, 1)
    else:
        deps = (deps, 0)

    return cakes, deps


def read_deps(g, namemap, linkname):
    """Read dependencies.

    Args:
        g (graph object): graph
        namemap (dictionnary): namemap linking linknames to vertex_index
        linkname (str): basename of the cookbookpage

    Returns:
        deps (list): List of all deps of the file



    """

    return [g.vp.smlk[v] for v in g.get_in_edges(namemap[linkname])[:, 0]]


def read_cakes(g, namemap, linkname):
    """Read cakes.

    Args:
        g (graph object): graph
        namemap (dictionnary): namemap linking linknames to vertex_index
        linkname (str): basename of the cookbookpage

    Returns:
        deps (list): List of all cakes of the file



    """
    return [g.vp.smlk[v] for v in g.get_out_edges(namemap[linkname])[:, 1]]


def get_cakes(file):
    """Make cakes.

    Wrapper to generate_trace_cake()
    Args:
        file (FileObject, str): filename in whatever form works for linking.FlexFile()
    Returns:
        cakes (list): List of all cakes of the file



    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    cakes = generate_trace_cake(filename, linkname, cookbookleftpage)
    dirname = os.path.dirname(filename)
    print("cakes in get_cakes*********************************")
    _cakes = []

    for c in cakes:
        if not os.path.isabs(c):
            _cakes.append(os.path.join(dirname, c))

    return _cakes


def get_deps(file, cakes):
    """Make deps.

    Run trace to find up to date deps list

    Args:
        file (FileObject, str): filename in whatever form works for linking.FlexFile()
    Returns:
        deps (list): List of all deps of the file



    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    deps = generate_trace_deps(filename, linkname, cookbookleftpage, cakes)
    print("deps in get_deps*********************************")
    dirname = os.path.dirname(filename)
    _deps = []
    for d in deps:
        if not os.path.isabs(d):
            _deps.append(os.path.join(dirname, d))
    print(_deps)
    return _deps


def generate_trace_cake(filename, linkname, cookbookleftpage):
    """Make cakes.

    Run trace to find up to date cake list

    Args:
        filename (FileObject, str): filename in whatever form works for linking.FlexFile()
        linkname (str):
        cookbookleftpage (str): absolute path to the node content file
    Returns:
        cakes (list): List of all cakes of the file



    """
    logging.debug("Running trace cake on {}".format(cookbookleftpage))
    g, namemap = graph.open_graph()
    trace = g.vp.trace[namemap.get(linkname)]
    file = generate_builder_file(trace)
    tracefile = run_trace(file, filename, cookbookleftpage, inout=1)
    return unmold_cake(tracefile, filename, level="fwpartition")


def generate_recipe(linkname):
    g, namemap = graph.open_graph()
    recipe = g.vp.recipe[namemap.get(linkname)]
    file = generate_builder_file(recipe)
    return file


def generate_interact(linkname):
    g, namemap = graph.open_graph()
    interact = g.vp.interact[namemap.get(linkname)]
    file = generate_builder_file(interact)
    return file


def generate_trace_deps(filename, linkname, cookbookleftpage, cakes):
    g, namemap = graph.open_graph()
    trace = g.vp.trace[namemap.get(linkname)]
    file = generate_builder_file(trace)
    tracefile = run_trace(file, filename, cookbookleftpage, inout=2)
    return _sort_out_trace(tracefile, cakes, filename, level="fwpartition")


def _sort_out_trace(tracefile, cakes, filename, level="fwpartition"):
    """Filter the tracefile for dependencies.

    Run the script on the symlink obtained from the cookbookpage, and filter out unneeded dependencies according to the given level. This method is called by generate_trace_deps.


    Args:
        tracefile (str): Absolute paths to the output of trace file.
        level (str): Filtering level. For now this is the only option that is provided.
        filename (str): The absolute path to the symlink.
        cakes (List): List of absolute paths to the cakes.

    Returns:
        deps (list): List of absolute paths to the dependencies


    """
    #### For now only dealing with dependencies at level inside /home/user/. Later might do more complex stuff to get further dependencies, such as librairies.
    print(tracefile)
    if level == "fwpartition":
        _str_header = PATH_TO_FW_PARTITION
    deps = []
    SHELL_NAME = "bash"
    passed_bash = False
    with open(tracefile, "r") as fd:
        for line in fd:
            # if SHELL_NAME in line:
            #     passed_bash = True

            # if passed_bash is True:
            #     line = line.rstrip("\n")

            #### Keep only:  (paths in userhome OR local), that are not also outputs, are not the actual file, and is not part of the Mlink system
            line = line.rstrip("\n")
            local_flag = False
            if os.path.basename(filename) in line or line[0] != "/":
                local_flag = True
            try:  #### This is not robust at all. Can be made better easily. For now keep in mind that a file name should not be names ......_v.....
                if (filename.split("_v")[0] in line) and (
                    filename.split("_v")[1].split(".")[0] in VERSION_NUMBER
                ):
                    copy_flag = True
                    logging.debug("I am tracing on a copy")
                else:
                    copy_flag = False
            except IndexError:
                copy_flag = False
            try:
                if line.split("_v")[0] == filename.split(".")[0]:
                    copy_flag_bis = True
                    logging.debug("I found a copy in the deps")
                else:
                    copy_flag_bis = False
            except IndexError:
                copy_flag_bis = False
            if (
                (
                    _str_header in line or local_flag
                )  ### If the trace-line is in the home folder, or in the local folder
                and not os.path.isdir(line)  ### If it is not a folder
                and (
                    line not in cakes
                )  ### If the trace-line is not the cakes (this means we run once for the cakes, then feed cakes to the second run for the dependencies)
                and (filename not in line)  ### If the trace-line is not the file itself
                and (
                    not (copy_flag or copy_flag_bis)
                )  ### If the trace-line is not a copy of the file
                and (
                    ".cookbook" not in line
                )  ### If the trace-line is not calling something from cookbook
                and (
                    not line.startswith(_str_header + "/.")
                )  ### If the trace-line is not a hidden file     ----> then it is a dependency or cake
            ):
                line = line.lstrip(".")
                if local_flag:
                    line = line.lstrip("/")
                deps.append(line)

    # os.remove(tracefile)

    return set(deps)


def generate_builder_file(build):
    file = PATH_TO_DUMP + str(random.uniform(1, 10000000)) + ".tmpbuilder.sh"
    with open(file, "w") as fd:
        fd.writelines([b + "\n" for b in build])
    os.chmod(file, 0o777)
    return file


def run_trace(script, symlink, leftcookbookpage, inout=3):
    """Execute trace script on symlink, with read, write or read-write tracking.

    (tracefile calls strace, which will slow down the process. A better solution might be to use perf, see http://www.brendangregg.com/perf.html)

    Args:
        _script (str): Absolute path to the script needed to run trace on cakes.
        symlink (str): Absolute path to the symbolic link to the left cookbookpage
        leftcookbookpage (str): The absolute path to the cookbookleftpage
        inout (int): R(ead)W(rite) in decimal form. e.g. only Read access is R = 1, W = 0, which is 2 in decimal form.

    Returns:
        dep_name (str): Absolute paths to the output of trace file.


    """
    dep_name = "/".join(
        [
            PATH_TO_DUMP,
            os.path.basename(leftcookbookpage) + str(random.uniform(1, 1000)) + "dep",
        ]
    )
    logger.info("Going to run script: {} with trace on {}".format(script, symlink))
    print("Going to run script: {} with trace on {}".format(script, symlink))
    bash_cmd = [f"bash {script} {symlink}"]
    # if inout == 3:
    #     _cmd = ["tracefile", "-u", "-e", "-f"] + bash_cmd
    # elif inout == 2:
    #     _cmd = ["tracefile", "-u", "-e", "-r", "-f"] + bash_cmd
    # elif inout == 1:
    #     _cmd = ["tracefile", "-u", "-e", "-w", "-f"] + bash_cmd

    _cmd = ["stracegawk"] + bash_cmd + [str(inout)]
    print(_cmd)
    with open(dep_name, "a") as fd:
        subprocess.call(_cmd, stdout=fd)
    return dep_name


def filter_out_cakes_for_deps(line, filename):
    g, namemap = graph.open_graph()
    t = namemap[linking.FlexFile(filename).linkname]
    in_edges = g.get_in_edges(g.vertex(t))
    try:
        s = namemap[linking.FlexFile(line).linkname]
    ### Line does not exist yet
    except OSError:
        return 1
    ### Line is not in the graph yet
    except KeyError:
        return 1

    _edge = [s, t]
    if (_edge == in_edges).all(axis=1).any():
        return 0
    return 1


def unmold_cake(tracefile, filename, level="fwpartition"):
    """Filter the output of the trace file.

    For now only dealing with dependencies at level inside /home/user/. Later might do more complex stuff to get further dependencies, such as librairies.

    Args:
        tracefile (str): Absolute paths to the output of trace file.
        level (str): Filtering level. For now this is the only option that is provided.

    Returns:
        cakes (list): List of the absolute paths to the cakes.


    """
    #### For now only dealing with dependencies at level inside /home/user/. Later might do more complex stuff to get further dependencies, such as librairies.
    if level == "fwpartition":
        _str_header = PATH_TO_FW_PARTITION
    cakes = []

    print("=================== starting trace for cake")
    with open(tracefile, "r") as fd:

        for line in fd:
            line = line.rstrip("\n")
            if line[0] == "/":  # absolute paths
                if (
                    (_str_header in line)
                    and (filter_out_cakes_for_deps(line, filename))
                    and (not os.path.isdir(line))
                    and (filename not in line)
                    and (".cookbook" not in line)
                    and (not line.startswith(_str_header + "/."))
                ):
                    cakes.append(line)
            else:  # realtive paths
                if (
                    not os.path.isdir(line)
                    and (".cookbook" not in line)
                    and (filter_out_cakes_for_deps(line, filename))
                ):
                    cakes.append(line)

    # os.remove(tracefile)
    return set(cakes)
