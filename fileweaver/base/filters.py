import os
import configparser



config = configparser.ConfigParser()
config.read(os.environ["CONFIG_FILE"])

PATH_TO_FW_PARTITION = config.get("FW-paths", "PATH_TO_FW_PARTITION")
VERSION_NUMBER = config.get("FW-values", "VERSION_NUMBER")
PATH_TO_DUMP = config.get("FW-paths", "PATH_TO_DUMP")

def filter_abspath(line, *args):
	return True if line[0] == "/" else False
	
def filter_relpath(line, *args):
	return False if line[0] == "/" else True

def filter_partition(line, *args):
	return True if PATH_TO_FW_PARTITION in line else False
	
def filter_partit_or_local(line, filename):
	return True if PATH_TO_FW_PARTITION in line or line[0] != "/" or os.path.basename(filename) in line else False
	
def filter_is_not_dir(line, *args):
	return True if not os.path.isdir(line) else False
	
def filter_filename_not_in_line(line, filename):
	return True if filename not in line else False
	
def filter_cookbook(line, *args):
	return True if not ".cookbook" in line else False
	
def filter_no_hidden_files(line, *args):
	return True if not line.startswith(PATH_TO_FW_PARTITION + "/.") else False
	
	
