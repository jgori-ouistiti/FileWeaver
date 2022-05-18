# Install script for Ubuntu 20.04 focal fossa

# install git
# sudo apt-get install git
# git clone https://github.com/jgori-ouistiti/FileWeaver


# Installing graph tool
echo 'deb [arch=amd64] https://downloads.skewed.de/apt focal main' | sudo tee -a /etc/apt/sources.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25
sudo apt-get update
sudo apt-get install python3-graph-tool -y

# make
sudo apt-get install make

# curl
sudo apt-get install curl -y

# venv
sudo apt-get install python3.8-venv -y
pip3 install pyzmq

# poetry
curl -sSL https://install.python-poetry.org | python3 -
echo "export PATH=\$PATH:~/.local/bin" >> ~/.bash_profile
source ~/.bash_profile
# install python packages with poetry, enable system-site-packages
poetry config virtualenvs.in-project true

#update
curl -sSL https://install.python-poetry.orgsudo apt update
sudo apt upgrade

poetry install
poetry update
poetry install
sed -i 's/include-system-site-packages = false/include-system-site-packages = true/g' .venv/pyvenv.cfg

# nautilus-python
sudo apt-get install python3-nautilus -y
mkdir -p ~/.local/share/nautilus-python/extensions/
export XDG_DATA_HOME=~/.local/share/
export NAUTILUS_PYTHON_DEBUG=misc
ln -s fileweaver/scripts/linked_menu.py ~.local/share/nautilus-python/extensions/linked_menu.py
##### Useful but not strictly needed
# netstat for sudo netstat -lntp
sudo apt-get install net-tools
sudo apt-get install nemo -y


