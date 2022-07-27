from fileweaver.base import graph
from fileweaver.base import linking
from fileweaver.base import cooking
from fileweaver.base import managing
from fileweaver.read_write import readwrite

import gensim
from gensim.models.doc2vec import Word2Vec, Doc2Vec, TaggedDocument
import numpy as np

import json

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])
path = config.get("Main","PATH_TO_LIBS")

def map_incoming_message_from_websocket(msg):
    print(msg)
    line = msg.rstrip("\n").split(",")

    # logging.info(line)
    #### Single file operations
    if "addFileAndChildren" in line[0]:
        # logging.info("addFileAndChildren")
        print("addFileAndChildren")
        file = line[1]
        print("file", file)
        cooking.add_file_and_children(file)

    elif "copyFileWithDependencies" in line[0]:
        # logging.info("copyFileWithDependencies")
        file = line[1]
        managing.copy_link(file)

    elif "makeStandaloneArchiveRun" in line[0]:
        # logging.info("makeStandaloneArchiveRun")
        file = line[1]
        managing.make_archive(file, mode="full", runnable=True)

    elif "makeStandaloneArchiveFlat" in line[0]:
        # logging.info("makeStandaloneArchiveFlat")
        file = line[1]
        managing.make_archive(file, mode="full", runnable=False)

    elif "editFileAndUpdate" in line[0]:
        # logging.info("editFileAndUpdate")
        file = line[1]
        cooking.edit_linked_file(file)

    elif "removeFileAsLink" in line[0]:
        # logging.info("removeFileAsLink")
        file = line[1]
        managing.un_link(file)

    elif "tagFile" in line[0]:
        # logging.info("tagFile")
        file = line[1]
        managing.tag_link(file)
    elif "showInFileBrowser" in line[0]:
        # logging.info("showInFileBrowser")
        file = line[1]
        managing.call_naut(file)

    #### Multifile operations
    elif "connectFiles" in line[0]:
        # logging.info("connectFiles")
        files = line[1:]
        managing.attach_link(files)

    elif "disconnectFiles" in line[0]:
        # logging.info("disconnectFiles")
        files = line[1:]
        managing.detach_link(files)

    elif "morphFiles" in line[0]:
        # logging.info("morphFiles")
        files = line[1:]
        managing.morph(files)

    elif "tagGroupOfFiles" in line[0]:
        # logging.info("tagGroupOfFiles")
        files = line[1:]
        managing.grouptag_links(files)
    elif "CompareFiles" in line[0]:
        # logging.info("CompareFiles")
        filename = line[1]
        versions = line[2:]
        # nautgit.show_diff_versions(filename, versions)
	

    elif "editKeywords" in line[0]:
        parsed_msg = json.loads(msg)
        file = linking.FlexFile(parsed_msg[1])
        graph.update("vertex","keywords",file._get()[1],parsed_msg[3])
        #keywords
        model = Word2Vec.load(path + "word2vec_openintro-statistics.bin")
        vec = []
        for k in parsed_msg[3]:
            vec.append(model.wv.get_vector(k))
        vec = list(np.array(vec).sum(axis=0)/len(vec)) if len(vec) != 0 else [0]
        zero = np.zeros(len(vec)).tolist()
        print(f"vec {type(vec)}")
        print(f"zero {type(zero)}")
        graph.update("vertex", "keywordvec", file._get()[1], zero)
        graph.vectorize_nodes()
        print("update finished")

    else:
        print(line)
        print(
            "command not found. don't forget to change this when connecting to the node js part for real."
        )

        # logging.info("unknown command")
        # logging.info(line)
