import gi

gi.require_version("Nautilus", "3.0")
from gi.repository import Gtk


from fileweaver.read_write import readwrite
from fileweaver.base import graph
from fileweaver.base import linking
from fileweaver.base import graph
from fileweaver.git_integration import nautgit


import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_LOG = config.get("FW-paths", "PATH_TO_LOG")
IMG_FORMATS = config.get("FW-values", "IMG_FORMATS")
VID_FORMATS = config.get("FW-values", "VID_FORMATS")
PATH_TO_FILES = config.get("FW-paths", "PATH_TO_FILES")


import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(PATH_TO_LOG)
# fh = logging.StreamHandler(sys.stdout)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

import subprocess
import sys
import stat
import time
import shutil
import numpy


def do_this(file):
    print(file)


## Morphing stuff


def morph_decorator(function):
    """Call this decorator before an action that needs a file to be unmorphed."""

    def morph_function_wrapper(file):
        filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
            file
        )._get()
        g, namemap = graph.open_graph()
        try:
            uses_morph_flag = g.vp.flags[namemap[linkname]][3]  # if uses morph
        except KeyError:
            print("keyerror")
            uses_morph_flag = linking.uses_morph(file)
        if uses_morph_flag:
            logging.debug("I noticed that file {} uses morphs".format(filename))
            linehacks, symlinks, hidden_copy = actions_unmorph(filename)
            args = function(file)
            function.symlinks = symlinks
            actions_remorph(filename, symlinks, hidden_copy)
            return args

        else:
            logging.debug("this file does not use morphs")
            return function(file)

    return morph_function_wrapper


def actions_remorph(filename, symlinks, hidden_copy):
    """Restore the file that was here before the unmorph procedure

    Args:
        filename (FileObject): name of file that was unmoprhed
        symlinks (list): list of symlinks to remove
        hidden_copy (filename): hidden copy that was created during unmorphing

    Returns:
        None
    """
    filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
        filename
    )._get()
    cmd = "cat {} > {}".format(hidden_copy, cookbookleftpage)
    subprocess.call(cmd, shell=True)
    ##Clean up
    for link in symlinks:
        os.remove(link)


def actions_unmorph(filename):
    """Unmorph procedure

    unmorph() is the minimum set of actions.
    hack_unmoprh() has to be called whenever the file: filename processes extensions, and the extension has to be tricked.

    Args:
        filename (FileObject): name of file that was unmoprhed

    Returns:
        linehacks, symlinks, hidden_copy: inputs to actions_remoprh
    """
    abs_path_gf, linehacks, wanted_index, extension = unmorph(filename)
    filename, hidden_copy, symlinks = hack_unmorph(
        filename, abs_path_gf, linehacks, wanted_index, extension
    )
    return linehacks, symlinks, hidden_copy


def unmorph(filename):
    """Unmorph procedure

    Call find_preferred_extension() to have get the extension format needed in filename. Also produce stuff for the remorph procedure.

    Args:
        filename (FileObject): name of file that was unmoprhed

    Returns:
        abs_path_gf(str):  absolute path of the generic file that is needed
        linehacks(dictionnary): key=string to replace; value = replacement string
        wanted_file_index: vertex_index of generic file
        queried_extension: extension format of the generic file in this filename
    """
    ### only coded for images
    linehacks = {}
    filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
        filename
    )._get()
    with open(filename, "r") as fd:
        for line in fd:
            if ".gifc" in line:
                #### Find out to which file the gifc should point to
                (
                    line,
                    abs_path_gf,
                    generic_file_found,
                    queried_extension,
                    wanted_file_index,
                ) = find_preferred_extension(filename, line.split(".gifc")[0] + ".gifc")

                logging.debug(
                    "I found that {} uses morph {}".format(filename, generic_file_found)
                )

                #### Give out all the linehacks that are needed in case hacking is needed (i.e. a .gifc extension disrupts the process)
                queried_extension = "." + queried_extension

                linehacks[line] = line.replace(".gifc", queried_extension)

                g, namemap = graph.open_graph()
                abs_path_target = g.vp.smlk[wanted_file_index].replace(
                    queried_extension, ".gifc"
                )
                abs_path_source = g.vp.path[wanted_file_index]
                unsafe_symlink(abs_path_source, abs_path_target)

    try:
        return abs_path_gf, linehacks, wanted_file_index, queried_extension
    except UnboundLocalError:
        logging.error("Managing: unmorph:: I think no line with .gifc was found")
        ### Print out to terminal
        return abs_path_gf, linehacks, wanted_file_index, queried_extension


def unsafe_symlink(source, target):
    """Make a symlink, replace target if it already exists

    Args:
        source (str):
        target (str):

    Returns:
        1 if successful
    """
    try:
        os.symlink(source, target)
    except OSError:
        if os.path.exists(target):
            os.remove(target)
            os.symlink(source, target)

        else:
            ### Just to cast error to terminal
            logging.error("There was an error with unsafe_symlink:")
            os.symlink(source, target)

    return 1


def hack_unmorph(filename, abs_path_gf, linehacks, wanted_index, queried_extension):
    """Hack Unmorph procedure

    Copy the file, replace the generic files with the ones with the found extensions, and add symlinks.
    Args:
        filename (FileObject): name of file that was unmoprhed
        abs_path_gf, linehacks, wanted_index, queried_extension: see unmoprh()
    Returns:
        filename, hidden_copy, symlinks: see remoprh
    """
    symlinks = []
    g, namemap = graph.open_graph()
    ## Make a symlink with the good extension name
    source = g.vp.path[wanted_index]
    target = g.vp.smlk[wanted_index]
    unsafe_symlink(source, target)
    symlinks.append(target)

    ### Copy the original file and change the lines that call the geenric file
    filename = linking.FlexFile(filename).filename
    ### protect original file with copy2, to keep metadata & permissions
    hidden_copy = "/".join(
        [os.path.dirname(filename), "." + os.path.basename(filename)]
    )
    shutil.copy2(filename, hidden_copy)
    for key, value in zip(linehacks.keys(), linehacks.values()):
        cmd = "sed 's#{}#{}#g' <{} >.tmp.sed; cat .tmp.sed >{}".format(
            key, value, filename, filename
        )
        subprocess.call(cmd, shell=True)

    return filename, hidden_copy, symlinks


def find_preferred_extension(filename, line):
    """Find prefered extension


    Args:
        filename (FileObject): name of file that was unmoprhed
        line (str): line where .gifc was found
    Returns:
        line, abspath, gfname, queried_extension, index: see unmorph()
    """
    g, namemap = graph.open_graph()
    filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
        filename
    )._get()

    ### Step 1: Find the generic file and line
    source_found = False
    while line:
        if os.path.islink(line):  ### If the line matches an existing generic file
            source_found = line
            break
        elif os.path.islink(
            "/".join([os.path.dirname(filename), line])
        ):  #### Idem, but if the call to the generic file is local
            source_found = "/".join([os.path.dirname(filename), line])
            break
        else:
            line = line[1:]

    if not source_found:
        logging.error("Did not find the generic file you are calling.")
        exit()

    #### At this point, we have found the generic file,which is contained in line / souce_found
    generic_file_found = source_found
    ### The generic file points to one vertex in the graph; from there we can extract the morph group to which it belongs
    gfname, glname, gcbkpg, gcbklpg = linking.FlexFile(generic_file_found)._get()
    vertex_index = namemap[glname]

    morph_groups = g.vp.flags.get_2d_array([2])
    index = numpy.array([u for u in range(0, morph_groups.size)])
    if morph_groups[0][vertex_index] == -1:
        index = index[
            numpy.logical_or(
                vertex_index == morph_groups, vertex_index == index
            ).tolist()[0]
        ]
    else:
        index = sorted(
            index[(morph_groups[0][vertex_index] == morph_groups)[0]].tolist()
            + [morph_groups[0][vertex_index]]
        )
    ### index now has the vertex indexes of the files that belong to the morph group of the generic file
    ## Get index list, extension list  of the morph group
    index_list, ext_list = map(
        list, zip(*[(v, g.vp.smlk[v].split(".")[-1]) for v in index])
    )

    ### Now, look at existing in_edges: if one of the edges is contained in the morph group, return that one. Else, use the default file to figure out which morph to prioritize
    in_edges_indexes = g.get_in_edges(g.vertex(namemap[linkname]))[:, 0]

    for index in index_list:
        if index in in_edges_indexes:
            abspath = g.vp.path[index]
            queried_extension = abspath.split(".")[-1]
            return line, abspath, gfname, queried_extension, index

    logging.debug(
        "I did not find an existing edge between {} and the morphgroup".format(filename)
    )

    #### If the previous block did not exit the function, no existing edge between any of the morphgroup-files and the file exist. Look into the default file to see whether an extension should be prefered over the other.

    prefered_extension_list = linking.get_default_format_img(filename).split("/")

    while prefered_extension_list:
        ext = prefered_extension_list.pop(0)
        try:
            idx = ext_list.index(ext)
            if idx:
                abspath = g.vp.path[index_list[idx]]
                queried_extension = abspath.split(".")[-1]
                return line, abspath, gfname, queried_extension, index_list[idx]
        except ValueError:
            pass

    ### If the previous block still did not exit the function, then there is no way of knowing which actual file should be linked. Behavior is undefined as this point; one should probably query the user
    logging.error("I dont know which generic file instance to use")
    exit()


### Link creation stuff


def exists_decorator(function):
    """
    Call this decorator before a function which needs linked files
    """

    def exist_function_wrapper(file):
        filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
            file
        )._get()
        g, namemap = graph.open_graph()
        if not namemap.get(linkname):
            logging.debug("Exists Decorator: {} is not linked yet".format(filename))
            new_link(file)
            return function(file)
        else:
            logging.debug("{} is already linked".format(filename))
            return function(file)

    return exist_function_wrapper


def new_link(file, restore=True):
    """Make a new link."""

    try:
        FFobject = linking.FlexFile(file)
        filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
        
        FFobject.keyword_extract(3)
        params = FFobject.get_params()

        flags = [1, -2, -2]

        uses_morph = linking.uses_morph(file)
        if uses_morph is True:
            flags += [1]
        else:
            flags += [0]

        props = [
            cookbookleftpage,
            os.path.basename(filename),
            os.path.basename(filename),
            filename,
            flags,
            linking.get_default_recipe(filename),
            linking.get_default_trace(filename),
            linking.get_default_interact(filename),
            params
        ]

        print(f"paraaaaaaaams {props}")
        ret = graph.adding_vertex(props)
        if ret != -1:
            return create_link(filename)
        else:
            logging.info("Managing: File {} is already linked".format(filename))
        graph.vectorize_nodes()
        return cookbookpage
    except FileNotFoundError:
        print(f"new_link was called on file {file}, which does not exist anymore.")
        return None

    ### In case the file being called does not actually exist. (Maybe it eisted at some point and was deleted). If this happens it is probably caused by the morphing system, Let us simply check that the file exists and restore the symlink

    # except OSError:
    #     g, namemap = graph.open_graph()
    #     smlklist = g.vp.smlk.get_2d_array([0])[0].tolist()
    #     try:
    #         index = smlklist.index(file)
    #         path = g.vp.path[index]
    #         if restore is True:
    #             os.symlink(path, smlklist[index])
    #         return os.path.dirname(path)
    #     except ValueError:
    #         logging.error(
    #             "The file {} does not exist, either physically or somewhere in the graph. I am exiting".format(
    #                 file
    #             )
    #         )
    #         return -1


def un_link(file, restore=True):
    """Unlinks the file."""
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()

    graph.removing_vertex(cookbookleftpage)
    shutil.move(cookbookleftpage, filename)
    logger.info("Managing: Restored file in user space")
    return cookbookpage


def create_link(filename):
    """Creates a link from the absolute path of the file.

    Generate the cookbookpage name, create the corresponding folder, and fill in the left page. Creates the symbolic link to the file for the user to see. Initiates the Git repo in the cookbookpage.

    Args:
        filename (str): The absolute path to the file

    Returns:
        cookbookpage: Returns the absolute path of the cookbookpage

    """
    linkname = linking.generate_linkname(filename)  ## Devicenumber_InodeNumber
    cookbookpage = "/".join([PATH_TO_FILES, linkname])
    os.mkdir(cookbookpage)

    ## Create Cookbook Left Page
    cookbookleftpage = "/".join([cookbookpage, os.path.basename(filename)])
    shutil.move(filename, cookbookleftpage)
    if not os.path.isfile(cookbookleftpage):
        logger.error("Error moving the file {}".format(filename))
        exit()
    else:
        logger.info("Wrote left page of cookbook")

    ## Create invisible hard link to force inode to remain the same
    cmd = [
        "ln",
        cookbookleftpage,
        cookbookpage + "/." + os.path.basename(filename) + ".backup",
    ]
    subprocess.call(cmd)
    logger.info("Wrote hard link")
    ## Create symbolic link to old destination
    smlnk = ["ln", "-s", cookbookleftpage, filename]

    subprocess.call(smlnk)
    logger.info("Wrote symbolic link")

    ## Create a Git Repo
    nautgit.create_new_repo(cookbookpage, cookbookleftpage)
    logger.info("Created Git Repo")
    ## Rename branch

    return cookbookpage


#### Other menu commands


def a_time(file):
    """
    Returns access time of a file
    """
    FFobject = linking.FlexFile(file)
    return os.stat(FFobject.filename)[stat.ST_ATIME]


@exists_decorator
def add_morphlink(file):
    pass


def get_prefix_ext(files):
    """
    Returns common prefix of the selected files.
    """
    prefix = {}
    for file in files:
        _pre = ".".join(
            os.path.basename(linking.FlexFile(file).filename).split(".")[:-1]
        )
        _ext = linking.FlexFile(file).filename.split(".")[-1]
        if prefix.get(_pre) is None:
            prefix[_pre] = [_ext]
        else:
            prefix[_pre] += [_ext]
    return prefix


def add_morphs_to_graph(linknames, filenames):
    """Creates a link from the absolute path of the file.

    Updates the morph flags

    """

    g, namemap = graph.open_graph()
    ## Take all links, sort them by morph, to be sure that the first item is a morph
    _sorted = sorted(
        zip(linknames, filenames),
        key=lambda link_file: g.vp.flags[namemap[link_file[0]]][2],
    )

    ## Then, if first is a morph, all others will have its morph flag as their morph flag. Else, their morph flag will be its vertex number and its morph flag becomes -1
    for n, (link, file) in enumerate(_sorted):
        if n == 0:
            v_num = namemap[link]
            morph_flag = g.vp.flags[v_num][2]
            if morph_flag < -1:
                # g.vp.flags[v_num][2] = -1
                graph.update(
                    "vertex", "flags", link, -1, property_index=2, g=g, namemap=namemap
                )
            elif morph_flag > -1:
                v_num = morph_flag
            else:
                pass
        else:
            v_new = namemap[link]
            # g.vp.flags[v_new][2] = v_num
            graph.update(
                "vertex", "flags", link, v_num, property_index=2, g=g, namemap=namemap
            )
    ret = g.vp.path[v_num]
    graph.close_graph(g, namemap)
    return ret


def morph(files):

    """Morph files.

    Take all files and morph them. Remove all symlinks and replace them with a single generic symlink.

    Args:
        files (list): List of files (FileObject, filenames etc.)

    Returns:
        None

    """

    # cwd = os.getcwd()
    def sort_morph_hf(linkname, g, namemap):
        return g.vp.flags[namemap[linkname]][2]

    prefix = get_prefix_ext(files)

    linknames = []
    filenames = []
    for file in files:
        add_morphlink(file)
        filename, linkname, cookbookpage, cookbookleftpage = linking.FlexFile(
            file
        )._get()
        os.unlink(filename)
        filenames.append(filename)
        linknames.append(linkname)

    symlink_src = add_morphs_to_graph(linknames, filenames)
    cwd = os.path.dirname(
        filenames[0]
    )  #### This is not robust at all. This should later be fixed, once a rationale to find where to put the generic file.

    if len(prefix) == 1:
        prefix, exts = prefix.keys()[0], prefix.values()[0]
        imgflag = list(set(IMG_FORMATS) & set(exts))
        videoflag = list(set(VID_FORMATS) & set(exts))
        if len(imgflag) > len(videoflag):
            generic_format = "gifc"
            logging.debug("These morphs represent images")
        else:
            generic_format = "gvfc"
        os.symlink(symlink_src, "/".join([cwd, ".".join([prefix, generic_format])]))

    elif len(prefix) > 1:
        logging.info(
            "I guess this is nothing but a good old folder. For now I have not implemented this"
        )


def make_archive(file, mode="full", runnable=True):
    g, namemap = graph.open_graph()
    filename, linkname, _, _ = linking.FlexFile(file)._get()
    if namemap.get(linkname) is None:
        logging.warning("No archive for file that is not linked")
        return
    if mode == "full":
        _, _, _, components = graph.get_subgraph_belongs(
            linkname, index=False, g=g, namemap=namemap
        )
    elif mode == "below":  ### not done yet
        pass
    vertex_list = [ni for ni, i in enumerate(components.__array__()) if bool(i) is True]
    archivename = ".".join(filename.split(".")[:-1]) + "_standalone.zip"
    if runnable is False:
        cmd = "zip -q -r --junk-paths {}".format(archivename)
        for v in vertex_list:
            cmd += " {}".format(g.vp.path[v])

    else:
        cmd = "zip -q -r {}".format(archivename)
        for v in vertex_list:
            cmd += " {}".format(g.vp.smlk[v])
    subprocess.call(cmd.split(" "))
    return archivename


def grouptag_links(files):
    """
    Change the tag attribute of a node
    """

    win = nautgit.TextViewWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    g, namemap = graph.open_graph()
    with open(".msglog.txt", "r") as f:
        content = f.readline().rstrip(
            "\n"
        )  ### Whatever user types, tag is in the first line
    # g.vp.tag[namemap[cookbookpage.split('/')[-1]]] = content

    for file in files:
        cookbookpage = new_link(file)
        if not isinstance(cookbookpage, str):
            logging.error("Link is not established")
            return 0
        graph.update(
            "vertex", "tag", cookbookpage.split("/")[-1], content, g=g, namemap=namemap
        )
    graph.close_graph(g, namemap)


@morph_decorator
def tag_link(file):
    """
    Change the tag attribute of a node
    """
    print(" I am in tag")
    logging.info(" I am in tag")
    cookbookpage = new_link(file)
    if not isinstance(cookbookpage, str):
        logging.error("Link is not established")
        print("link not established")
        return 0
    logging.info("passed, I am in tag")
    logging.info("passed, I am in tag")
    win = nautgit.TextViewWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    g, namemap = graph.open_graph()
    with open(".msglog.txt", "r") as f:
        content = f.readline().rstrip(
            "\n"
        )  ### Whatever user types, tag is in the first line
    # g.vp.tag[namemap[cookbookpage.split('/')[-1]]] = content
    graph.update(
        "vertex", "tag", cookbookpage.split("/")[-1], content, g=g, namemap=namemap
    )
    graph.close_graph(g, namemap)


@exists_decorator
def copy_link(file):
    """
    Make a copy of the file that preserves in_edges (dependencies)
    """
    FFobject = linking.FlexFile(file)
    filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
    new_cookbookpage, new_cookbookleftpage, new_symlink = nautgit.add_working_branch(
        filename, linkname, cookbookpage, cookbookleftpage
    )
    graph.copy_node(linkname, new_cookbookleftpage, new_symlink)


def showdiff(files):
    if len(files) > 3:
        logging.error("Only comparing two or three files is supported for now")
        return -1
    else:
        leftpages = []
        titles = []
        for f in files:
            FFobject = linking.FlexFile(f)
            filename, linkname, cookbookpage, cookbookleftpage = FFobject._get()
            leftpages.append(cookbookleftpage)
            u = linking.get_version_number(os.path.basename(filename))
            if u:
                titles.append("Version-" + u)
            else:
                titles.append("Original")
        ttl_cmd = " ".join(
            ["--title" + str(ni + 1) + " " + i for ni, i in enumerate(titles)]
        ).split(" ")
        if len(files) == 2:
            diffcmd = ["xxdiff", "-wB", "--merge"] + ttl_cmd + leftpages
            subprocess.call(diffcmd)
        elif len(files) == 3:
            diffcmd = ["xxdiff", "--merge"] + ttl_cmd + leftpages
            subprocess.call(diffcmd)


def attach_link_decorator(function):
    def attach_function_wrapper(deps_or_cakes, file):
        ## Here we separate files that are manually connected (connected_files) with the ones that are automatically connected (keep_files) for a separate treatment

        g, namemap = graph.open_graph()

        w = namemap[linking.FlexFile(file).linkname]
        edges = g.get_all_edges(g.vertex(w), eprops=[g.ep.update_time])
        args = function(deps_or_cakes, file)
        if edges.size != 0:
            edges_manual = edges[edges[:, 2] == sys.float_info.max]
            edges_manual = edges_manual[edges_manual[:, 0] != edges_manual[:, 1]]
            if edges_manual.size != 0:
                update_manual_connection(edges_manual[:, 0:2])

        return args

    return attach_function_wrapper


def update_manual_connection(edges_manual):
    print("passing through update_manual_connection ****** with")
    print(edges_manual)
    for _edge in edges_manual:
        attach_link([_edge[0], _edge[1]], master=_edge[1], index=True)
    return 1


def attach_link(files, master=None, index=False):
    if len(files) > 2:
        logging.warning(
            "Warning: Managing: attach_link() is not designed yet to have more than one file connected to another. Will come soon"
        )

    ### if master is given, all other files are its parents (i.e. all other files point towards master)
    ### else:
    ### there is no parent to child relationship but a sibling relationship, and pick a source/target at random (case of two). If this were to change, deal with update_manual_connection() in managing.py
    if master is None:
        master = files[0]
        files.remove(master)
    else:
        files.remove(master)

    if index is False:
        for file in files:
            ret = new_link(file)
        ret = new_link(master)

    g, namemap = graph.open_graph()

    ## Deal with master
    if index is False:
        child_linkname = linking.FlexFile(master).linkname
        in_edges = g.get_in_edges(namemap[child_linkname])
    else:
        in_edges = g.get_in_edges(master)
    ## For each remaining file, create an edge with special values towrads master
    for file in files:
        flag_add = False
        if index is False:
            parent_linkname = linking.FlexFile(file).linkname
            _edge = [namemap[parent_linkname], namemap[child_linkname]]
        else:
            _edge = [file, master]

        if not (_edge == in_edges).all(axis=1).any():
            flag_add = True
            e = g.add_edge(*_edge)
            g.ep.update_bool[e] = 0
        else:
            e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
        g.ep.update_time[e] = sys.float_info.max
        g.ep.edge_dir_up[e] = bool(0)
        if index is False:
            vhash = g.vp.version[namemap[parent_linkname]]
        else:
            vhash = g.vp.version[file]
        g.ep.parent_version[e] = vhash

        edic = {}
        if flag_add is True:
            action = "add_edge"
            edic["update_bool"] = bool(0)
            edic["format"] = str("NA")
        else:
            action = "update_edge"

        edic["update_time"] = sys.float_info.max
        edic["edge_dir_up"] = bool(0)
        edic["parent_version"] = vhash
        _id = "{}#{}".format(_edge[0], _edge[1])
        if index is False:
            readwrite.send_instruction_over(parent_linkname, action, _id, {}, edic)
        else:
            readwrite.send_instruction_over(str(int(file)), action, _id, {}, edic)

    graph.close_graph(g, namemap)


def detach_link(files):
    if len(files) > 2:
        logging.warning(
            "Warning: Managing: attach_link() is not designed yet to have more than one file connected to another. Will come soon. detach_link() is therefore also working only for two files currently"
        )

    g, namemap = graph.open_graph()

    file = files[0]
    bestand = files[1]

    f_v = namemap[linking.FlexFile(file).linkname]
    b_v = namemap[linking.FlexFile(bestand).linkname]

    edges = g.get_all_edges(f_v)
    if ([f_v, b_v] == edges).all(axis=1).any():
        g.remove_edge(g.edge(g.vertex(f_v), g.vertex(b_v)))
        _id = "{}#{}".format(f_v, b_v)
        readwrite.send_instruction_over(
            linking.FlexFile(file).linkname, "delete_edge", _id
        )

    if ([b_v, f_v] == edges).all(axis=1).any():
        g.remove_edge(g.edge(g.vertex(b_v), g.vertex(f_v)))
        _id = "{}#{}".format(b_v, f_v)
        readwrite.send_instruction_over(
            linking.FlexFile(bestand).linkname, "delete_edge", _id
        )

    graph.close_graph(g, namemap)
    return 1


def call_naut(file):
    g, namemap = graph.open_graph()
    filename = linking.FlexFile(file).filename
    cmd = "nautilus -s {}".format(filename)
    logging.info("cmd printed")
    logging.info(cmd)
    subprocess.call(cmd.split(" "))
