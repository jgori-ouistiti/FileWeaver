import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk


from graph_tool import Graph, GraphView, load_graph
import graph_tool.topology as gtt
import graph_tool.draw as gtd
import pickle

import os
import configparser

config = configparser.RawConfigParser()
config.read(os.environ["CONFIG_FILE"])


PATH_TO_GRAPH = config["FW-paths"]["PATH_TO_GRAPH"]
PATH_TO_NAMEMAP = config["FW-paths"]["PATH_TO_NAMEMAP"]

from fileweaver.read_write import readwrite


import numpy

import logging

logger = logging.getLogger(__name__)


import multiprocessing

lock = multiprocessing.Lock()


vertex_properties = [
    ("path", "string"),
    ("tag", "string"),
    ("target", "string"),
    ("smlk", "string"),
    ("flags", "vector<int>"),
    ("recipe", "vector<string>"),
    ("interact", "vector<string>"),
    ("trace", "vector<string>"),
    ("status", "bool"),
    ("emptyout", "float"),
    ("emptyin", "float"),
    ("version", "string"),
    ("cluster", "string"),
]
edge_properties = [
    ("update_time", "float"),
    ("update_bool", "bool"),
    ("edge_dir_up", "bool"),
    ("format", "string"),
    ("parent_version", "string"),
]


def init_graph():
    """Start a new graph.

    For now, each call to the menu destroys the old graph, and calls init to create a new one.

    returns:
        1 if successful
    """

    if os.path.exists(PATH_TO_GRAPH) and os.path.exists(PATH_TO_NAMEMAP):
        logging.info("There is an existing graph and associated NameMap")
        return open_graph()

    print("Creating a new graph")

    g = Graph()

    g.vp.path = g.new_vertex_property(
        "string"
    )  # absolute path to content file (cookbook, hidden from user)
    g.vp.tag = g.new_vertex_property("string")  # user defined tag, by default basename
    g.vp.target = g.new_vertex_property(
        "string"
    )  # basename, makes sense to use if you want to display different tag + target
    g.vp.smlk = g.new_vertex_property(
        "string"
    )  # absolute path to symbolic link (what the user sees)
    g.vp.flags = g.new_vertex_property(
        "vector<int>"
    )  #### updateflag / copyflag / ismorphflag / usesmorphflag
    # updateflag: if 1 update
    # copyflag: if -1 is original of a copy, if -2 no copies exist, else vertex number of original
    # ismorphflag: if -2 is not a morph, if -1 is head of morphgroup vertex_index, if (int)v is part of morphgroup v
    # usesmorphflag: if 1 uses morph, else not
    g.vp.recipe = g.new_vertex_property(
        "vector<string>"
    )  # bash commands to run/compile file
    g.vp.trace = g.new_vertex_property(
        "vector<string>"
    )  # bash commands to run trace on file (usually recipe or dry-run version of recipe)
    g.vp.interact = g.new_vertex_property(
        "vector<string>"
    )  # bash script to interact with the file (usually just a call to the editor)
    g.vp.status = g.new_vertex_property(
        "bool"
    )  # If 1 then the node is linked, else it is unlinked. Restoring or removing a file is just a question of changing this flag
    g.vp.emptyout = g.new_vertex_property("double")
    g.vp.emptyin = g.new_vertex_property("double")
    g.vp.cluster = g.new_vertex_property("string")


    g.ep.update_time = g.new_edge_property("double")
    g.ep.edge_dir_up = g.new_edge_property("bool")
    g.ep.update_bool = g.new_edge_property("bool")
    # These are all used for update mechanics.
    g.ep.format = g.new_edge_property("string")
    # To store the generic file format preference
    g.vp.version = g.new_vertex_property("string")  # current git revision hash
    g.ep.parent_version = g.new_edge_property(
        "string"
    )  # store which revision hash was used

    name_map = {}

    ### Adding 2 vertices and an edge to the system to force graphml
    v = g.add_vertex()
    g.vp.path[v] = "NA"
    g.vp.tag[v] = "G"
    g.vp.target[v] = "G"
    g.vp.smlk[v] = "NA"
    g.vp.flags[v] = [1, 0, 0, 0]
    g.vp.recipe[v] = ["NA"]
    g.vp.trace[v] = ["NA"]
    g.vp.interact[v] = ["NA"]
    g.vp.emptyout[v] = 0
    g.vp.emptyin[v] = 0
    g.vp.status[v] = 1  ### This is a special node that can trigger actions
    g.vp.version[v] = "NA"
    g.vp.cluster[v] = "cat"

    w = g.add_vertex()
    g.vp.path[w] = "NA"
    g.vp.tag[w] = "NA"
    g.vp.target[w] = "NA"
    g.vp.smlk[w] = "NA"
    g.vp.flags[w] = [1, 0, 0, 0]
    g.vp.recipe[w] = ["NA"]
    g.vp.trace[w] = ["NA"]
    g.vp.interact[w] = ["NA"]
    g.vp.emptyout[w] = 0
    g.vp.emptyin[w] = 0
    g.vp.status[w] = 0
    g.vp.version[w] = "NA"
    g.vp.cluster[w] = "cat"

    e = g.add_edge(g.vertex(v), g.vertex(w))
    g.ep.update_time[e] = 0.0
    g.ep.edge_dir_up[e] = bool(0)
    g.ep.update_bool[e] = bool(0)
    g.ep.format[e] = "format"
    # To store the generic file format preference
    g.ep.parent_version[e] = "papa"

    g.save(PATH_TO_GRAPH)

    with open(PATH_TO_NAMEMAP, "wb") as fd:
        pickle.dump(name_map, fd, pickle.HIGHEST_PROTOCOL)
    return g, name_map


def copy_node(node_copied_from, node_copied_to_path, node_copied_to_symlink, send=True):
    """Copy a node in the graph.

    Not sure it is used anymore

    Args:
        node_copied_from (str): Linkname of the node from which we copy
        node_copied_to_path (str): path attribute of the copy.
        node_copied_to_symlink (str):  symlink attribute of the copy.

    Returns:
        new_v (int): vertex index of new node


    """
    g, namemap = open_graph()
    v = namemap[node_copied_from]

    ### Change copy flag to indicate this file has been copied
    # g.vp.flags[v][1] = -1
    update(
        "vertex", "flags", node_copied_from, -1, property_index=1, g=g, namemap=namemap
    )

    ### Vertex properties for copy
    _tag = g.vp.tag[v].split(".")
    _tag = ".".join([_tag[0] + "_vB", _tag[-1]])
    _flags = [1, v, g.vp.flags[v][2], g.vp.flags[v][3]]

    props = [
        node_copied_to_path,
        _tag,
        g.vp.target[v],
        node_copied_to_symlink,
        _flags,
        g.vp.recipe[v],
        g.vp.trace[v],
        g.vp.interact[v],
        g.vp.cluster[v],
    ]

    new_v, g, namemap = adding_vertex(props, True, g, namemap)

    # updating in edges in graph and remote
    ## Get edge information from original node
    in_edges = g.get_in_edges(
        v, eprops=[g.ep.update_time, g.ep.edge_dir_up, g.ep.update_bool]
    )
    new_in_edges = numpy.copy(
        in_edges
    )  # Make sure modifying one doesn't touch the other
    new_in_edges[:, 1] = [new_v.__int__() for i in in_edges[:, 1]]

    for _edge in new_in_edges[:, 0:2]:
        e = g.add_edge(int(_edge[0]), int(_edge[1]))
        action = "add_edge"
        _id = "{}#{}".format(int(_edge[0]), int(_edge[1]))
        readwrite.send_instruction_over(node_copied_from, action, _id, {}, {})

    # Get parentversion ep, since can't be accessed by eprops above (not scalar array)

    for _edge in in_edges:
        e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
        new_e = g.edge(g.vertex(_edge[0]), g.vertex(new_v.__int__()))
        g.ep.parent_version[new_e] = g.ep.parent_version[e]
        g.ep.format[new_e] = g.ep.format[e]
        ## send message at the same time, since we are already looping over edges
        if send is True:
            action = "update_edge"
            edic = {}
            edic["update_time"] = _edge[2]
            edic["edge_dir_up"] = bool(_edge[3])
            edic["parent_version"] = str(g.ep.parent_version[e])
            edic["update_bool"] = bool(_edge[4])
            edic["format"] = str(g.ep.format[e])
            _id = "{}#{}".format(int(_edge[0]), new_v.__int__())
            readwrite.send_instruction_over(
                os.path.dirname(g.vp.path[new_v]).split("/")[-1], action, _id, {}, edic
            )

    close_graph(g, namemap)
    return new_v


def open_graph():
    """Open and return the graph.

    Args:


    Returns:
        g (graph object): graph
        namemap (dictionnary): dictionnary which links linkname to graph vertex index


    """

    # g = load_graph(PATH_TO_GRAPH, fmt="auto")
    g = load_graph(
        PATH_TO_GRAPH, fmt="auto", ignore_vp=None, ignore_ep=None, ignore_gp=None
    )
    # g.set_vertex_filter(g.vp.status)
    with open(PATH_TO_NAMEMAP, "rb") as fd:
        namemap = pickle.load(fd)
    return g, namemap


def close_graph(g, namemap):
    """Save and close the graph.

    Args:
        g (graph object): graph
        namemap (dictionnary): dictionnary which links linkname to graph vertex index

    Returns:
        1 if successful


    """

    # g.save(PATH_TO_GRAPH, fmt = "auto")
    g.save(PATH_TO_GRAPH)
    with open(PATH_TO_NAMEMAP, "wb") as fd:
        pickle.dump(namemap, fd, pickle.HIGHEST_PROTOCOL)
    return 1


def remote_dispatch(id, action, vdic, edic, g, namemap):
    if action == "add":
        return remote_add_vertex(id, vdic, g, namemap)
    if action == "add_edge":
        return remote_add_edge(id, edic, g, namemap)
    ##below untested
    if action == "update_edge":
        return remote_update_edge(id, edic, g, namemap)
    if action == "delete_edge":
        return remote_delete_edge(id, edic, g, namemap)


def remote_delete_edge(id, edic, g, namemap):
    s, t = id.split("#")
    g.remove_edge(g.edge(g.vertex(s), g.vertex(t)))
    return True, g, namemap


def remote_update_edge(id, edic, g, namemap):
    s, t = id.split("#")
    e = g.edge(g.vertex(s), g.vertex(t))

    g.ep.edge_dir_up[e] = bool((edic["edge_dir_up"]))
    g.ep.update_time[e] = float(edic["update_time"])
    g.ep.parent_version[e] = edic["parent_version"]
    return True, g, namemap


def remote_add_edge(id, edic, g, namemap):
    s, t = id.split("#")
    in_edges = g.get_in_edges(g.vertex(t))
    _edge = [g.vertex(s), g.vertex(t)]
    if not (_edge == in_edges).all(axis=1).any():
        e = g.add_edge(g.vertex(s), g.vertex(t))
        g.ep.update_bool[e] = bool(1)
        g.ep.update_time[e] = float(edic["update_time"])
        g.ep.parent_version[e] = edic["parent_version"]
        g.ep.edge_dir_up[e] = bool((edic["edge_dir_up"]))
    return True, g, namemap


def remote_add_vertex(id, vdic, g, namemap):
    if float(id) != float(g.get_vertices().size - 1):
        path = vdic["path"]
        tag = vdic["tag"]
        target = vdic["target"]
        smlk = vdic["smlk"]
        flags = vdic["flags"]
        recipe = vdic["recipe"]
        trace = vdic["trace"]
        interact = vdic["interact"]
        cluster = vdic["cluster"]
        props = path, tag, target, smlk, flags, recipe, trace, interact, cluster
        return adding_vertex(props, False, g, namemap)
    return True, g, namemap


def adding_vertex(props, send=True, *args):
    """Add vertex to the graph.

    If args is None, then the graph and namemap are loaded using open_graph(), else graph and namemap are read from args[0] and args[1]

    Args:
        props (list): node attributes (path, tag, target, smlk, flags, recipe, trace, interact)
        args[0] (graph object): graph
        args[1] (dictionnary): namemap

    Returns:
        1 if successful


    """
    print(f"propos \n {props}")
    path, tag, target, smlk, flags, recipe, trace, interact, cluster = props
    linkname = os.path.dirname(path).split("/")[-1]
    FLAG_OPENED = 0
    try:
        g, namemap = args[0], args[1]
    except IndexError:
        FLAG_OPENED = 1
        g, namemap = open_graph()
    v = namemap.get(linkname)

    if v is None:
        v = g.add_vertex()
        logging.info(
            "Graph: Added vertex {} with linkname: {} and tag: {}".format(
                v, linkname, tag
            )
        )
        namemap[linkname] = v.__int__()
    else:
        if not g.vp.status[v]:
            logging.info(
                "Graph: This vertex is abandoned, will reclaim it. At this point, I should remove all existing edges before reclaiming, for now this is missing "
            )
            ###Drop all edges to and from this vertex
        else:
            logging.info("Graph: Vertex already exists")
            return -1

    g.vp.path[v] = str(path)
    g.vp.tag[v] = str(tag)
    g.vp.target[v] = str(tag)
    g.vp.smlk[v] = str(smlk)

    #### Deal here with the mini language.

    if isinstance(flags, str):
        g.vp.flags[v] = [
            float(int(f)) for f in flags.rstrip("]").lstrip("[").split(",")
        ]
    else:
        g.vp.flags[v] = flags

    if isinstance(recipe, str):
        g.vp.recipe[v] = recipe.rstrip("]").lstrip("[").split(",")
    else:
        g.vp.recipe[v] = recipe

    if isinstance(trace, str):
        g.vp.trace[v] = trace.rstrip("]").lstrip("[").split(",")
    else:
        g.vp.trace[v] = trace

    if isinstance(interact, str):
        g.vp.interact[v] = interact.rstrip("]").lstrip("[").split(",")
    else:
        g.vp.interact[v] = interact

    if isinstance(cluster, str):
        g.vp.cluster[v] = cluster.rstrip("]").lstrip("[").split(",")
    else:
        g.vp.cluster[v] = cluster

    g.vp.emptyout[v] = 0
    g.vp.emptyin[v] = 0
    g.vp.status[v] = 1

    if send == True:
        vdic = {}
        vdic["path"] = str(path)
        vdic["tag"] = str(tag)
        vdic["target"] = str(target)
        vdic["smlk"] = str(smlk)
        vdic["flags"] = flags
        vdic["recipe"] = str(recipe)
        vdic["trace"] = str(trace)
        vdic["interact"] = str(interact)
        vdic["cluster"] = str(cluster)
        vdic["emptyout"] = 0
        vdic["emptyin"] = 0
        vdic["status"] = 1
        readwrite.send_instruction_over(linkname, "add", v, vdic)

    if FLAG_OPENED:
        close_graph(g, namemap)
        return v.__int__()
    else:
        return v.__int__(), g, namemap


def removing_vertex(cookbookleftpage):
    """Remove vertex from the graph.

    Remove a vertex from the graph, by changing its status flag (node can always be recoevered by changing its status.)

    Args:
        cookbookleftpage (list): path to file to be removed


    Returns:
        1 if successful


    """
    linkname = os.path.dirname(cookbookleftpage).split("/")[-1]
    g, namemap = open_graph()
    # g.vp.status[namemap[linkname]] = 0
    update("vertex", "status", linkname, 0, g=g, namemap=namemap)
    close_graph(g, namemap)
    return 1


def get_subgraph_belongs(linkname, index=False, g=None, namemap=None):
    """Identify the component (graph) to which linkname belongs.

    Args:
        linkname (str/int): linkname or vertex index of the node
        index (bool): if False the expect linkname as string, else as vertex  index

    Returns:
        g (graph object): graph
        namemap (dictionnary): map linking linkname to vertex_index
        subg (graph object): component


    """
    if g is None or namemap is None:
        g, namemap = open_graph()
        print("I am opening the graph")
    else:
        print("I am using the graph supplied")
    components, histogram = gtt.label_components(g, directed=False)
    if (
        index is False
    ):  ### Use this if linkname input is the actua linkname (i.e. directory of cookbookpage)
        if namemap.get(linkname) is not None:
            components_subgraph = components.a == components.a[namemap[linkname]]
            subg = GraphView(g, components_subgraph)
        else:
            subg = g
            components_subgraph = None

    else:  ### Use this to provide the index of the vertex
        try:
            components_subgraph = components.a == components.a[linkname]
            subg = GraphView(g, components_subgraph)
        except KeyError:
            subg = g
            components_subgraph = None
    return g, namemap, subg, components_subgraph


def update(property_type, property_name, linkname, value, **kwargs):
    # Open graph if it is not provided
    LOAD_GRAPH = 0
    g = kwargs.get("g")
    namemap = kwargs.get("namemap")
    if g is None or namemap is None:
        LOAD_GRAPH = 1
        g, namemap = open_graph()

    ## If vertex  do vertex stuff
    if property_type == "v" or property_type == "vertex":
        property_type_string = "Vertex"
        property_index = kwargs.get("property_index")
        if property_index is None:
            g.vp[property_name][namemap[linkname]] = value
            dic_entry = value
        else:
            g.vp[property_name][namemap[linkname]][property_index] = value
            dic_entry = [v for v in g.vp[property_name][namemap[linkname]]]
        id = namemap[linkname]
        vdic = {}
        vdic[property_name] = dic_entry

    ## if edge do edge stuff --- has to be adapted
    elif property_type == "e" or property_type == "edge":
        property_type_string = "Edge"
        property_index = kwargs.get("property_index")
        if property_index is None:
            g.ep[property_name][namemap[linkname]] = value
        else:
            g.ep[property_name][namemap[linkname]][property_index] = value

    ## Close graph if it was opened before
    if LOAD_GRAPH:
        close_graph(g, namemap)

    ## Print out message to console
    if property_index is None:
        print(
            "Updated {}-{} for vertex {} ({}) to value {}".format(
                property_type_string,
                property_name,
                namemap[linkname],
                g.vp.tag[namemap[linkname]],
                value,
            )
        )
    else:
        print(
            "Updated {}-{}[{}] for vertex {} ({}) to value {}".format(
                property_type_string,
                property_name,
                property_index,
                namemap[linkname],
                g.vp.tag[namemap[linkname]],
                value,
            )
        )

    ## Write out stuff
    readwrite.send_instruction_over(linkname, "update", id, vdic)

    return 1


def get_subgraph_spawns(linkname, index=False):
    """Get out components of the node (cakes).

    Args:
        linkname (str/int): linkname or vertex index of the node
        index (bool): if False the expect linkname as string, else as vertex  index

    Returns:
        g (graph object): graph
        namemap (dictionnary): map linking linkname to vertex_index
        subg (graph object): component


    """
    g, namemap = open_graph()
    if index is False:
        components = gtt.label_out_component(g, g.vertex(namemap[linkname]))
    else:  ### Use this to provide the index of the vertex
        components = gtt.label_out_component(g, g.vertex(linkname))
    subg = GraphView(g, components)
    return g, namemap, subg


def button_press_fct(widget, event):
    g = widget.graph.g
    if g.num_vertices() == 0:
        return

    if (
        widget.graph.is_zooming
        or widget.graph.is_rotating
        or widget.graph.is_drag_gesture
    ):
        return

    if event.button == 1 and event.state & Gdk.ModifierType.CONTROL_MASK:
        widget.graph.init_picked()
        _picked = widget.graph.picked
        print("\nPicked Vertex Number {}".format(_picked))

        in_edges = g.get_in_edges(_picked)
        out_edges = g.get_out_edges(_picked)
        print("in edges:")
        for _edge in in_edges:
            e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
            for key, value in g.edge_properties.items():
                print("{} \t {}".format(key, value[e]))
            print("\n")
        print("\n\n")
        print("out edges:")
        for _edge in out_edges:
            e = g.edge(g.vertex(_edge[0]), g.vertex(_edge[1]))
            for key, value in g.edge_properties.items():
                print("{} \t {}".format(key, value[e]))
            print("\n")
        print("\n\n\n")

    elif event.button == 1:
        widget.graph.init_picked()
        _picked = widget.graph.picked
        print("\nPicked Vertex Number {}".format(_picked))
        for key, value in g.vertex_properties.items():
            print("{} \t {}".format(key, value[_picked]))
        print("\n")


_window_list = []


def informative_window(
    g,
    pos=None,
    vprops=None,
    eprops=None,
    vorder=None,
    eorder=None,
    nodesfirst=False,
    geometry=(500, 400),
    update_layout=True,
    sync=True,
    main=True,
    **kwargs
):
    if pos is None:
        if update_layout:
            pos = gtd.random_layout(g, [1, 1])
        else:
            pos = gtd.sfdp_layout(g)
    win = gtd.GraphWindow(
        g,
        pos,
        geometry,
        vprops,
        eprops,
        vorder,
        eorder,
        nodesfirst,
        update_layout,
        **kwargs
    )

    win.connect("button_press_event", button_press_fct)
    win.show_all()
    _window_list.append(win)
    if main:
        if not sync:
            # just a placeholder for a proper main loop integration with gtk3 when
            # ipython implements it
            import IPython.lib.inputhook

            f = lambda: Gtk.main_iteration_do(False)
            IPython.lib.inputhook.set_inputhook(f)
        else:

            def destroy_callback(*args, **kwargs):
                global _window_list
                for w in _window_list:
                    w.destroy()
                Gtk.main_quit()

            # win.connect("delete_event", destroy_callback)
            win.connect("delete_event", Gtk.main_quit)
            # Gtk.main()
    return pos, win.graph.selected.copy()


def draw_graph(*args):
    """Draw graph.

    If graph is called without arguments, it will plot the whole graph, else it will plot args[0]

    Args:
        args[0] (graph object): graph to be plotted

    Returns:
        None


    """
    if not args:
        g, namemap = open_graph()
    else:
        g = args[0]
    edge_color = g.new_edge_property("vector<double>")
    edge_label = g.new_edge_property("string")
    g.ep.edge_color = edge_color
    g.ep.edge_label = edge_label
    for e in g.edges():
        if g.ep.parent_version[e] == g.vp.version[e.source()]:
            edge_color[e] = (0, 0, 0, 1)
            edge_label[e] = " "
        else:
            edge_color[e] = (0, 0, 0, 0.5)
            edge_label[e] = g.ep.parent_version[e][:7]
    pos, selected = informative_window(
        g, vertex_text=g.vp.tag, edge_color=edge_color, edge_text=g.ep.edge_label
    )
