import gi

gi.require_version("Nautilus", "3.0")
from gi.repository import Nautilus, GObject

##### Indicate here where to find the submodules nautilusGit, parameters, read_write and tools

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])
PATH_TO_LIBS = config.get("Main", "PATH_TO_LIBS")
PATH_TO_SHARED_FILE = config.get("Main", "PATH_TO_SHARED_FILE")
PATH_TO_LOG = config.get("FW-paths", "PATH_TO_LOG")
import sys

sys.path.append(PATH_TO_LIBS)


from fileweaver.base import graph
from fileweaver.base import linking
from fileweaver.base import cooking
from fileweaver.base import managing

from fileweaver.read_write import readwrite
from fileweaver.git_integration import nautgit


import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# fh = logging.FileHandler(PATH_TO_LOG)
fh = logging.StreamHandler(sys.stdout)

fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


import pickle


### Open file for logs
import os

os.makedirs(os.path.dirname(PATH_TO_LOG), exist_ok=True)
with open(PATH_TO_LOG, "w") as tmp_f:
    pass


import multiprocessing
import stat


class ExampleMenuProvider(
    GObject.GObject, Nautilus.MenuProvider, Nautilus.InfoProvider, Nautilus.FileInfo
):
    def __init__(self):
        pass

    def update_file_info(self, file):
        pass

    def get_file_items(self, window, files):

        top_menuitem = Nautilus.MenuItem(
            name="ExampleMenuProvider::Links", label="Links", tip="Links"
        )

        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        #### Read the selected file(s) and write them to the shared file
        linknames = [linking.FlexFile(file).linkname for file in files]
        print(linknames)
        readwrite.send_view_over(linknames)

        if len(files) == 1:

            #### Edit
            sub_editLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::EditLinks", label="Edit", tip="Edit"
            )
            submenu.append_item(sub_editLink)
            sub_editLink.connect("activate", self.activate_edit_link, files[0])

            #### Add
            sub_addLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::AddLinks", label="Add", tip="Add"
            )
            submenu.append_item(sub_addLink)
            sub_addLink.connect("activate", self.activate_add_link, files[0])

            ### Version Tree
            sub_ShowVersionTree = Nautilus.MenuItem(
                name="ExampleMenuProvider::ShowVersionTree",
                label="Show Version Tree",
                tip="Show Version Tree",
            )
            submenu.append_item(sub_ShowVersionTree)
            sub_ShowVersionTree.connect(
                "activate", self.activate_show_version_tree, files[0]
            )

            #### New Link
            sub_newLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::NewLink", label="New Link", tip="New Link"
            )
            submenu.append_item(sub_newLink)
            sub_newLink.connect("activate", self.activate_new_link, files[0])

            #### Remove Link
            sub_rmLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::RmLink",
                label="Remove Link",
                tip="Remove Link",
            )
            submenu.append_item(sub_rmLink)
            sub_rmLink.connect("activate", self.activate_rm_link, files[0])

            #### Copy Link
            sub_cpLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::CpLink", label="Copy Link", tip="Copy Link"
            )
            submenu.append_item(sub_cpLink)
            sub_cpLink.connect("activate", self.activate_cp_link, files[0])

            #### Tag Link
            sub_tagLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::tagLink", label="Tag Link", tip="Tag Link"
            )
            submenu.append_item(sub_tagLink)
            sub_tagLink.connect("activate", self.activate_tagLink, files[0])

            #### test Link
            sub_testLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::testLink", label="Test Link", tip="Test Link"
            )
            submenu.append_item(sub_testLink)
            sub_testLink.connect("activate", self.activate_testLink, files[0])

            sub_archiveLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::archive",
                label="Make Standalone Archive",
                tip="Make Standalone Archive",
            )
            submenu.append_item(sub_archiveLink)

            subsubmenu_archive = Nautilus.Menu()
            sub_archiveLink.set_submenu(subsubmenu_archive)

            run_arxiv = Nautilus.MenuItem(
                name="ExampleMenuProvider::subarchive1",
                label="Runable Archive",
                tip="Runable Archive",
            )
            flat_arxiv = Nautilus.MenuItem(
                name="ExampleMenuProvider::subarchive2",
                label="Flat Archive",
                tip="Flat Archive",
            )

            subsubmenu_archive.append_item(run_arxiv)
            subsubmenu_archive.append_item(flat_arxiv)

            run_arxiv.connect("activate", self.activate_makearchive_run, files[0])
            flat_arxiv.connect("activate", self.activate_makearchive_flat, files[0])

        else:
            sub_FuseLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::FuseCopies",
                label="Fuse Copies",
                tip="Fuse Copies",
            )
            submenu.append_item(sub_FuseLink)
            sub_FuseLink.connect("activate", self.activate_fuse_link, files)

            sub_ShowDiffLink = Nautilus.MenuItem(
                name="ExampleMenuProvider::Show Difference",
                label="Show Difference",
                tip="Show Difference",
            )
            submenu.append_item(sub_ShowDiffLink)
            sub_ShowDiffLink.connect("activate", self.activate_showdiff_link, files)

            sub_MorphFiles = Nautilus.MenuItem(
                name="ExampleMenuProvider::MorphFiles",
                label="Morph Files",
                tip="Morph Files",
            )
            submenu.append_item(sub_MorphFiles)
            sub_MorphFiles.connect("activate", self.activate_morph, files)

            sub_connect_files = Nautilus.MenuItem(
                name="ExampleMenuProvider::ConnectFiles",
                label="Connect Files",
                tip="Connect Files",
            )
            submenu.append_item(sub_connect_files)
            sub_connect_files.connect("activate", self.activate_connect_files, files)

            sub_disconnect_files = Nautilus.MenuItem(
                name="ExampleMenuProvider::DisconnectFiles",
                label="Disconnect Files",
                tip="Disconnect Files",
            )
            submenu.append_item(sub_disconnect_files)
            sub_disconnect_files.connect(
                "activate", self.activate_disconnect_files, files
            )

            sub_grouptag_files = Nautilus.MenuItem(
                name="ExampleMenuProvider::TagGroup", label="Tag Group", tip="Tag Group"
            )
            submenu.append_item(sub_grouptag_files)
            sub_grouptag_files.connect("activate", self.activate_grouptag_files, files)

        return (top_menuitem,)

    ## Single file selected

    def activate_add_link(self, menu, file):
        cooking.add_file_and_children(file)
        graph.draw_graph()

    def activate_new_link(self, menu, file):
        linkname = managing.new_link(file)
        graph.draw_graph()

    def activate_rm_link(self, menu, file):
        ret = managing.un_link(file)
        if isinstance(ret, str):
            logger.info("Removed meal with ID {}\n\n".format(ret))
        else:
            logger.error("Did not unlink file")

    def activate_edit_link(self, menu, file):
        cooking.edit_linked_file(file)
        graph.draw_graph()
        # nautgit.plot_repo(file)

    def activate_tagLink(self, menu, file):
        managing.tag_link(file)
        graph.draw_graph()

    def activate_cp_link(self, menu, file):
        managing.copy_link(file)
        graph.draw_graph()
        # nautgit.plot_repo(file)

    def activate_show_version_tree(self, menu, file):
        nautgit.plot_repo(file)

    def activate_testLink(self, menu, file):
        hash = nautgit.get_current_repo_version(file)

    def activate_makearchive_run(self, menu, file):
        archivename = managing.make_archive(file, mode="full", runnable=True)

    def activate_makearchive_flat(self, menu, file):
        archivename = managing.make_archive(file, mode="full", runnable=False)

        #### Multiple files selected

    def activate_connect_files(self, menu, files):
        managing.attach_link(files)
        # graph.draw_graph()

    def activate_morph(self, menu, files):
        managing.morph(files)
        graph.draw_graph()

    def activate_disconnect_files(self, menu, files):
        managing.detach_link(files)
        graph.draw_graph()

    def activate_fuse_link(self, menu, files):
        print("not activated yet ")
        return
        managing.fuse_link(files)

    def activate_showdiff_link(self, menu, files):
        managing.showdiff(files)

    def activate_grouptag_files(self, menu, files):
        managing.grouptag_links(files)
        graph.draw_graph()

    def get_background_items(self, window, file):
        pass
