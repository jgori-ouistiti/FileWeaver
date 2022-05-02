import gi

gi.require_version("Nautilus", "3.0")
from gi.repository import Gtk


import subprocess
import os

from fileweaver.base import graph
from fileweaver.base import linking
from fileweaver.read_write import readwrite

import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_FILES = config.get("FW-paths", "PATH_TO_FILES")
VERSION_NUMBER = config.get("FW-values", "VERSION_NUMBER")
PATH_TO_DUMP = config.get("FW-paths", "PATH_TO_DUMP")
PATH_TO_KITCHEN = config.get("FW-paths", "PATH_TO_KITCHEN")


import logging

logger = logging.getLogger(__name__)


class TextViewWindow(Gtk.Window):
    """Multi Line text Editing window for commit message


    Opens a window. Upon clicking on save, this message is written to a temporary file for later use. Subclassed from Gtk.Window

    Args:
        None

    Returns:
        None



    """

    def __init__(self):
        Gtk.Window.__init__(self, title="TextView Example")

        self.set_default_size(500, 350)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        toolbar = Gtk.Toolbar()

        save_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE)
        save_btn.connect("clicked", self.on_save_clicked)
        toolbar.insert(save_btn, 1)
        self.box.pack_start(toolbar, False, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        scrolledwindow.add(self.textview)
        self.box.pack_start(scrolledwindow, True, True, 0)

    def on_save_clicked(self, widget):
        save_file = ".msglog.txt"
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        text = self.textbuffer.get_text(start_iter, end_iter, True)
        with open(save_file, "w+") as f:
            f.write(text)


def _remain(func):
    """Decorator function to revert path to the one before doing the Git stuff



    Args:
        func (Function): name of the function to be wrapped.

    Returns:
        func return



    """

    def function_wrapper(*args):
        pwd = os.environ["PWD"]
        return func(*args)
        os.chdir(pwd)

    return function_wrapper


@_remain
def commit_and_update_graph(options=" ", file_or_folder=None):
    """Update the node version property in the graph everytime a commit is done.

    Args:
        file (FlexFile): anything that FlexFile recognizes as a file
        message(str): commit message
        file_or_folder (str): The absolute path to the cookbookpage (i.e. the repository folder) or something that works with FlexFile. If is None, then it is assumed that the cwd is the right one.
    Returns:
        None
    """
    if file_or_folder is not None:
        try:
            if os.path.isdir(file_or_folder):
                os.chdir(file_or_folder)
        except TypeError:
            cookbookpage = linking.FlexFile(file_or_folder)._get()[2]
            os.chdir(cookbookpage)

    git_cmd = "git commit " + options
    subprocess.call(git_cmd.split(" "))
    hash = get_current_repo_version()
    g, namemap = graph.open_graph()
    linkname = os.getcwd().split("/")[-1]
    # g.vp.version[linkname] = hash
    graph.update("vertex", "version", linkname, hash, g=g, namemap=namemap)
    graph.close_graph(g, namemap)
    return 1


@_remain
def create_new_repo(repo, file):
    """Create new Git repository inside the cookbookpage.
    Args:
        repo (str): The absolute path to the cookbookpage (i.e. the repository folder)
        files (list): List of strings of files to add to the repo

    Returns:
        None

    """
    os.chdir(repo)
    git_cmd = ["git", "init"]
    subprocess.call(git_cmd)
    git_cmd = ["git", "add"]
    # for f in files:
    #     git_cmd += [f]
    git_cmd += [file]
    subprocess.call(git_cmd)
    commit_and_update_graph("-m Versioned_Link_Creation", repo)


@_remain
def show_diff_versions(filename, versions):
    os.chdir(os.path.dirname(repo))
    if len(versions) != 2:
        print("Can only compare two files currently.")
        return -1
    gitcmd = "git difftool --gui --no-prompt {} {} {}".format(
        versions[0], versions[1], filename
    )
    subprocess.call(gitcmd.split(" "))
    return 1


@_remain
def get_diff_versions_stat(filename, versions):
    os.chdir(os.path.dirname(repo))
    if len(versions) != 2:
        print("Can only compare two files currently.")
        return -1
    gitcmd = "git diff --minimal --shortstat {} {} {}".format(
        versions[0], versions[1], filename
    )
    ret = subprocess.check_output(gitcmd.split(" ")).decode("utf-8").rstrip("\n")
    return ret


@_remain
def get_current_repo_version():
    """Read the git version hash.


    Args:
        None

    Returns:
        revision (str): hash of the revision
    """

    cmd = "git rev-list -n 1 HEAD"
    return subprocess.check_output(cmd.split(" ")).decode("utf-8").rstrip("\n")


@_remain
def read_logmsg_repo(repo, n=1):
    """Read the n-last message of the Git log.

    Args:
        repo (str): The absolute path to the cookbookpage (i.e. the repository folder)
        n (int): Number of messages to go back up to

    Returns:
        None


    """
    os.chdir(repo)
    git_cmd = ["git", "log", "--format=%B", "-n", str(n)]
    return subprocess.check_output(git_cmd).decode("utf-8").rstrip("\n")


@_remain
def commit_to_repo(repo):
    """Commit to git repo with a commit message queried by a UI. Could pass this to auto-generated text; or at least use auto-generated commit message as a suggestion to the user (Could also be stats on the diff).

    Args:
        repo (str): The absolute path to the cookbookpage (i.e. the repository folder)

    Returns:
        None


    """
    os.chdir(repo)

    git_cmd = "git diff > {}tmp.diff".format(PATH_TO_DUMP)
    subprocess.call(git_cmd, shell=True)
    # output = subprocess.check_output(git_cmd).decode("utf-8")
    with open("{}tmp.diff".format(PATH_TO_DUMP), "r") as fd:
        output = fd.readlines()
    win = TextViewWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    commit_and_update_graph("-a -F .msglog.txt")
    return output


@_remain
def get_worktree_branches(repo):
    """Get number of worktree branches.

    Args:
        repo (str): The absolute path to the cookbookpage (i.e. the repository folder)
        files (list): List of strings of files to add to the repo

    Returns:
        nbranches (int): Number of worktree branches


    """

    os.chdir(repo)
    git_cmd = ["git", "worktree", "list"]
    wc_cmd = ["wc", "-l"]
    pgit = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    pwc = subprocess.Popen(wc_cmd, stdin=pgit.stdout, stdout=subprocess.PIPE)
    pgit.stdout.close()
    nbranches = int(float(pwc.communicate()[0].decode("utf-8").rstrip("\n")))
    return nbranches


@_remain
def add_working_branch(filename, linkname, cookbookpage, cookbookleftpage):
    """Add a worktree branch (used in a copy) to the repo.

    Currently this works only for a single copy.

    Args:
        filename (str):
        linkname (str):
        cookbookpage (str):
        cookbookleftpage (str):

    Returns:
        None


    """
    repo = cookbookpage
    nbranch = get_worktree_branches(repo)
    ### No previous work trees
    if nbranch == 1:
        vers_num = VERSION_NUMBER[nbranch]
        filename_split = os.path.basename(filename).split(".")
        new_filename = ".".join(
            ["".join(filename_split[:-1]) + "_v" + vers_num, filename_split[-1]]
        )

        ### Add a git worktree branch: makes a new dir called %new_filename in repo, which contains  a.git + old filename
        git_cmd = ["git", "worktree", "add", "-b", vers_num, new_filename]

        subprocess.call(git_cmd)
        logging.info("Adding branch {} to {}".format(vers_num, cookbookleftpage))

        linkname = linking.generate_linkname(
            "/".join([repo, new_filename, os.path.basename(filename)])
        )

        cookbookpage = "/".join([PATH_TO_FILES, linkname])
        git_mv = ["git", "worktree", "move", new_filename, cookbookpage]

        subprocess.call(git_mv)

        cookbookleftpage = "/".join([cookbookpage, os.path.basename(filename)])
        ## Create invisible hard link to force inode to remain the same
        cmd = [
            "ln",
            cookbookleftpage,
            cookbookpage + "/." + os.path.basename(filename) + ".backup",
        ]
        subprocess.call(cmd)

        renamed_cookbookleftpage = "/".join([cookbookpage, new_filename])
        os.chdir(cookbookpage)
        cmd = ["mv", cookbookleftpage, renamed_cookbookleftpage]
        subprocess.call(cmd)
        cmd = "git rm {}; git add {}; git commit -m 'Copy Link'".format(
            cookbookleftpage, renamed_cookbookleftpage
        )
        subprocess.call(cmd, shell=True)

        cmd = ["rm", cookbookpage + "/." + os.path.basename(filename) + ".backup"]

        cmd = [
            "ln",
            renamed_cookbookleftpage,
            cookbookpage
            + "/."
            + os.path.basename(renamed_cookbookleftpage)
            + ".backup",
        ]
        subprocess.call(cmd)
        logger.info("Wrote hard link")

        ## Create symbolic link to old destination|||| Design choice to be discussed later on: should original and copy appear as two files or not ?
        smlnk = [
            "ln",
            "-s",
            renamed_cookbookleftpage,
            "/".join([os.path.dirname(filename), new_filename]),
        ]
        subprocess.call(smlnk)
        logger.info("Wrote symbolic link")
        return (
            cookbookpage,
            cookbookleftpage,
            "/".join([os.path.dirname(filename), new_filename]),
        )
    elif nbranch >= 1:
        logging.error(
            "case with more than two copies not treated for now, will add later"
        )
        exit()


@_remain
def repo_update(repos):
    """Update repository.

    I am not sure this function is actually used anymore. Just issues a commit if needed.

    Args:
        repos (list): list of repos to update

    Returns:
        None


    """

    for repo in repos:
        os.chdir(repo)
        git_cmd = "git status -uno --porcelain".split(" ")
        output = subprocess.check_output(git_cmd).decode("utf-8").rstrip("\n")
        if output:
            logging.info("I am updating the cookbookpage; out of date:")
            print(output)
            commit_to_repo(repo)
    return 1


@_remain
def plot_repo(object):
    """Plot git repository

    Calls a script git2dot.py found online to output a svg map of the graph.

    Args:
        object (repo/file/filename): Something to identify the repository.

    Returns:
        None


    """

    try:
        os.chdir(object)
    except TypeError:
        file = object
        FFobject = linking.FlexFile(file)
        os.chdir(FFobject.cookbookpage)
    cmd = "/home/jgori/Documents/Python/libs/missinglinklib/nautilusGit/git2dot.py -l '%s|%cr' --svg git.dot"
    subprocess.call(cmd.split(" "))
    cmd = "eog git.dot.svg"
    subprocess.call(cmd.split(" "))
    return


@_remain
def rename_branch(repo, oldname, newname):
    """Rename a branch.

    Not sure it is used anymore

    Args:
        repo (str): Location of the git repo
        oldname (str): old branch name
        newname (str):  new branch name

    Returns:
        None


    """
    os.chdir(repo)
    cmd = "git branch -m {} {}".format(oldname, newname)
    subprocess.call(cmd.split(" "))
    return


@_remain
def rename_local_working_copy(repo, oldname, newname):
    """Rename the working copy.

    Not sure it is used anymore

    Args:
        repo (str): Location of the git repo
        oldname (str): old file name
        newname (str):  new file name

    Returns:
        None


    """
    os.chdir(repo)
    cmd = "git mv {} {}".format(oldname, newname)
    subprocess.call(cmd.split(" "))
    cmd = "git commit -m 'renamed local working copy'"
    subprocess.call(cmd, shell=True)
    return


@_remain
def switch_branch(repo, branchname):
    if attr == "format":
        os.chdir(repo)
        cmd = "git checkout branchname"
        subprocess.call(cmd.split(" "))
    return


@_remain
def switch_format_branch(repo, branch):
    os.chdir(repo)
    cmd = "git checkout {}".format(branch)
    subprocess.call(cmd.split(" "))
    return


@_remain
def check_format_branch(repo, extension):
    os.chdir(repo)
    cmd = "git branch --list *{}".format(extension)
    return subprocess.check_output(cmd.split(" ")).decode("utf-8")


@_remain
def new_format(repo, extension, filename, cookbookleftpage):
    _script = "/".join([PATH_TO_KITCHEN, "new_format_git.sh"])
    options = " ".join([repo, extension, filename, cookbookleftpage])
    _cmd = " ".join([_script, options])
    subprocess.call(_cmd.split(" "))
    print("adding format {}".format(extension))
    return 1


##### This is from an old version and shouldn't work anymore. Has to be adapted.
def merge_two_worktrees(
    repo_main, repo_branch, interactive="no", which="theirs", branch="B"
):
    """Merge two checked out branches.

    Merge two working copies from two cjeckedout branches (via git worktree).

    Args:
        repo_main (str): Location of the original git repo
        repo_branch (str): location of the worktree branch git repo
        interactive (str): if "yes", a graphical merge tool is called if there is a conflict. If no, the conflict is automatically solved using 'theirs' rule (assumes the original copy is always right.)
        branch (str):  worktree branch name to be merged with the main. Only B for now.

    Returns:
        None


    """

    ### If interactive mode is no, order is: repo1 = main, repo2 = branch
    ### Catch symbolic link while repo still exists
    symlink = linking.find_smlink_from_cookbookpage(repo_branch)
    smlink_main = linking.find_smlink_from_cookbookpage(repo_main)
    ### Merge and destroy branch
    os.chdir(repo_main)
    if interactive == "no":
        #### Use git-fmt-merge-msg to create an auto merge msg
        cmd = (
            "git merge --stat --log -m 'merged auto-msg' -s recursive -X"
            + which
            + " "
            + str(branch)
        )
        logging.info("Calling merge")
        subprocess.call(cmd.split(" "))
    elif interactive == "yes":
        #### Finish this. For now, stuck on: 'hint: waiting for your editor to close the file'
        logging.info("Going to merge in interactive mode")
        cmd = "git merge " + str(branch)
        output_status = 1
        k = 0
        while output_status != 0:
            if k:
                cmd = "git merge --continue"
            try:
                output_status = (
                    subprocess.check_output(cmd.split(" ")).decode("utf-8").rstrip("\n")
                )
            except subprocess.CalledProcessError:  # , _exception:
                logging.info("Automerge was not successful:")
                print(_exception.returncode, _exception.output)
                if "CONFLICT" in _exception.output:
                    cmd = "git mergetool --tool=xxdiff"
                    subprocess.call(cmd.split(" "))
        k += 1
    else:
        pass

    logging.info("Deleting version-{}".format(branch))
    cmd = " ".join(["git worktree remove --force", repo_branch])
    subprocess.call(cmd.split(" "))
    cmd = "git branch -D {}".format(branch)
    subprocess.call(cmd.split(" "))

    logging.info("Removing Symbolic link to version-{}".format(branch))
    os.remove(symlink)
    cookbookleftpage, cookbookrightpage = linking.get_cookbook_pages(repo_main)
    readwrite.write_smlink_to_cookbookrightpage([smlink_main], cookbookrightpage)
    cookbookpage = linking.update_cookbookpage_name(repo_main)
    return cookbookpage
