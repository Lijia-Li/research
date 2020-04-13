"""Utility functions for processing the files"""

from os import listdir
from os.path import exists as file_exists, join as join_path, dirname, realpath

from ast import literal_eval

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


def get_rules(path):
	"""get rules dictionary from the file path
	
	Arguments:
		path {path} -- path to rules
	
	Returns:
		[dict{(tuples)}] -- {root: (rule, rule)}
	"""
	with open("./rules.txt") as f: 
		dict = literal_eval(f.read().strip())
	
	return dict


def censor(token):
	"""lemmatize the token, and agreegate person pronoun to -PRON-
	
	Arguments:
		token {token of NLP doc} -- a parsed token of document
	
	Returns:
		[string] -- a lemmatized, lowercased string
	"""
	# change person reference to PP
	if token.ent_type_ == 'PERSON': 
		return "-PRON-"
	# for all others, get lemmatizer
	# specifically, if the token is a "She, he, it", will be parsed as -PRON- as well
	else: 
		return token.lemma_.lower()
	
