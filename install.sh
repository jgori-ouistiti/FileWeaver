# Install script for Ubuntu 20.04 focal fossa

# Installing 
deb [ arch=amd64 ] https://downloads.skewed.de/apt focal main
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25
sudo apt-get install python3-graph-tool
sudo apt-get install python3-nautilus

# poetry
curl -sSL https://install.python-poetry.org | python3 -

# install python packages
poetry config virtualenvs.in-projet true
poetry install
sed -i 's/include-system-site-packages = false/include-system-site-packages = true/g' .venv/pyvenv.cfg
