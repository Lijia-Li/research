"""Utility functions for processing the files"""

from os import listdir
from os.path import exists as file_exists, join as join_path, dirname, realpath

def get_filelist_from_folder(directory):
    """yield directory/filename from given folder"""
    for filename in listdir(directory):
        if not filename.startswith("."):
            yield join_path(directory, filename)


def get_sentence_from_file(file):
	"""yield sentence from a single file
	
	Arguments:
		file {[str]} -- [the path of the file]
	
	Yields:
		[str] -- [a trimed sentence, splited by "."]
	"""
	for line in open(file, encoding='utf-8'):
	    sentence_ls = line.replace("\"", "").split(". ")
	    for sentence in sentence_ls:
	        yield sentence