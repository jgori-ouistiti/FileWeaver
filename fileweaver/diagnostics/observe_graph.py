import os

##### Indicate here where to find the submodules nautilusGit, parameters, read_write and tools
import configparser

config = configparser.RawConfigParser()
config.read("../../conf.cfg")
PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")
PATH_TO_SHARED_FILE = config.get("Main", "PATH_TO_SHARED_FILE")

import sys

sys.path.append(PATH_TO_LIBS)

### Make needed folders


from fileweaver.base import graph
import graph_tool

g, namemap = graph.open_graph()

g.ep.edge_color = g.new_edge_property("vector<double>")
g.ep.edge_label = g.new_edge_property("string")
for e in g.edges():
    if g.ep.parent_version[e] == g.vp.version[e.source()]:
        g.ep.edge_color[e] = (0, 0, 0, 1)
        g.ep.edge_label[e] = " "
    else:
        g.ep.edge_color[e] = (0, 0, 0, 0.5)
        g.ep.edge_label[e] = g.ep.parent_version[e][:7]

graph_tool.draw.graph_draw(
    g, vertex_text=g.vp.tag, edge_color=g.ep.edge_color, edge_text=g.ep.edge_label
)
