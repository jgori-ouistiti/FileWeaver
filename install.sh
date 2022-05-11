# Install script for Ubuntu 20.04 focal fossa

# install git
sudo apt-get install git
git clone https://github.com/jgori-ouistiti/FileWeaver

# Installing graph tool
echo 'deb [arch=amd64] https://downloads.skewed.de/apt focal main' | sudo tee -a /etc/apt/sources.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25
sudo apt-get update
sudo apt-get install python3-graph-tool -y
sudo apt-get install python3-nautilus -y

# make
sudo apt-get install make

# curl
sudo apt-get install curl -y

# venv
sudo apt-get install python3.8-venv -y

# poetry
curl -sSL https://install.python-poetry.org | python3 -
echo "export PATH=\$PATH:~/.local/bin" >> ~/.bash_profile
source ~/.bash_profile
# install python packages
poetry config virtualenvs.in-project true
poetry install
sed -i 's/include-system-site-packages = false/include-system-site-packages = true/g' .venv/pyvenv.cfg


