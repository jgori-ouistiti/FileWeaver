.. quickstart:

Quick Start
===============


.. To run FileWeaver, you will have to install graph-tool, nautilus-python and poetry:

    
..     * To install graph-tool, visit `graph-tool's documentation <https://git.skewed.de/count0/graph-tool/-/wikis/installation-instructions>`_


..     * Nautilus-python is an extension to Gnome Nautilus to write Python extensions for Nautilus, that FileWeaver uses as entry point in Ubuntu. To install nautilus-python, make sure you install the Python3 version:

..     .. code-block:: bash

..         # sudo apt-get install gir1.2-gconf-2.0 # likely not needed
..         sudo apt-get install python3-nautilus

        

..     .. Below not needed since there is a packaged version

..     .. * To install nautilus-python, DO NOT use the version in the APT repository (it is the deprecated Python 2 version). Instead, go to the `projet's repository<https://gitlab.gnome.org/GNOME/nautilus-python>`_, and download the source code. First you need to install autoconf, and its dependencies. The list below is needed on a standard Ubuntu 20.04 LTS install, you may need more libraries. 


..     .. First make sure autoconf is running:

..     .. .. code-block:: bash

..     ..     sudo apt-get install autoconf
..     ..     sudo apt-get install libtool
..     ..     sudo apt-get install gtk-doc-tools



..     .. You will likely need some extra dependencies for configure to run successfully:

..     .. .. code-block:: bash

..     ..     sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev # you can try without these ones
..     ..     sudo apt-get install libgirepository1.0-dev # you can try without these ones as well
..     ..     sudo apt install python-gi-dev
..     ..     sudo apt-get install libnautilus-extension-dev

..     .. Then, make sure the PYTHON env variable points towards python3, and run autoreconf && make && make install:

..     .. .. code-block:: bash
        
..     ..     export PYTHON='/usr/bin/python3'
..     ..     autoreconf -i
..     ..     make
..     ..     make install


..     Make sure Nautilus-Python knows where to find the Python scripts.
    
..     .. code-block:: bash

..         mkdir -p ~/.local/share/nautilus-python/extensions/
..         export XDG_DATA_HOME=~/.local

..     Make sure the extensions work, by trying out one of the `examples <https://gitlab.gnome.org/GNOME/nautilus-python/-/tree/master/examples>`_ that are known to work.

..     If that does not work, run Nautilus with ``NAUTILUS_PYTHON_DEBUG=misc``, and look where the extension looks for files

..     .. code-block:: bash

..         export NAUTILUS_PYTHON_DEBUG=misc

..     Finally, add a symbolic link to FileWeaver's entry point file in Nautilus:

..     .. code-block:: bash

..             # From FileWeaver repository
..             ln -s fileweaver/scripts/linked_menu.py ~/.local/share/nautilus-python/extensions/linked_menu.py

..     * Poetry is a Python package manager, that is used to manage Fileweaver dependencies. To install poetry, follow the instructions on the `projects' website <https://python-poetry.org/docs/#installation>`_.



.. I also recommend installing nemo:

..     * Since during development you will be closing and opening Nautilus a lot, it is useful to have another file manager. Nemo is a lightweight system which integrates well with GNOME:

..     .. code-block:: bash

..         sudo apt-get install nemo


First usage / Install
--------------------------

* git clone the FileWeaver repository

.. code-block:: bash

    sudo apt-get install git # if needed
    git clone https://github.com/jgori-ouistiti/FileWeaver/


* run the install script

.. code-block:: bash

    bash install.sh

* Log out / Log in (optional)


* Edit the ``conf.ini`` file. You have to give the path to the FileWeaver library you just cloned, and the path to a folder where FileWeaver will operate. An example would be:

.. code-block:: ini

    [Library]
    PATH_TO_LIBS = /home/user/Documents/FileWeaver/
    [FileWeaver_Partition]
    FW_PARTITION=/home/user/Documents/FileWeaver_Partition


* Run ``configure.py``, which creates a conf.cfg file and various scripts. 

.. code-block:: bash

    python3 configure.py

You can check what is inside that conf.cfg file, it indicates the location of various FileWeaver components.

* Open the poetry shell:

.. code-block:: bash

    poetry shell

This will put you in the virtual python environment with the correct packages installed. If your system is unable to find poetry, this is probably because you didn't relog in the session. Either do so or run

.. code-block:: bash

    source ~/.bash_profile

* Run ``run_fileweaver.py``. This will launch the server that forwards Fileweaver messages incoming from Nautilus over a websocket, and receives messages that it passes to Nautilus. This will also launch a Nautilus instance with Fileweaver support. From there, you can head to your FileWeaver partition and start experimenting.


Some tips
------------

* A ``requirements.txt`` and a ``setup.py`` can be created with Poetry (e.g. to install via pip):

.. code-block:: bash

    poetry export --without-hashes --dev -f requirements.txt --output requirements.txt

* FileWeaver uses a TCP socket on port 5555. If closed unproperly, the TCP socket will remain open. The launch script takes care of this, but should you still have a ``zmq.error.ZMQError: Address already in use``, you can 


.. code-block:: bash

    netstat -lntp # Look up sockets, identify the PID <pid> holding socket with port 5555 open
    kill -9 <pid>

* The nautilus window of FileWeaver uses websocket to forward information to the other windows via ``ws://localhost:4000``.

