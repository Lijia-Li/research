# Corpus Class
# 	1. Corpus Folder Path
#	2. Cached txt Folder Path (tokenized)
# 	3. Prob files path 
# 	4. hook up SQL file

# FUNCTIONS
# 	1. Get files from corpus folder
# 	2. 

# FOLDER LAYOUT
# dump 
# |----corpus
# |----stats
#		 |---- NP
#		 |---- VP
# 		 |---- cashed_prob
#		 |---- sql_prob

from utils import *

class Corpus:
	"""a class to wrap around corpus, including corpus and their data"""
	def __init__(self, dump_dir):
		self.dump_dir = dump_dir

		self.corpus_dir = join_path(self.dump_dir, "corpus")
		self.stats_dir = join_path(self.dump_dir, "stats")

		self.NP_extract_dir = join_path(self.stats_dir, "NP")  # pylint: disable=invalid-name
		self.VP_extract_dir = join_path(self.stats_dir, "VP")  # pylint: disable=invalid-name
		self.cashed_prob = join_path(self.stats_dir, "cashed_prob")
		self.sql_prob = join_path(self.stats_dir, "sql_prob")
    
	def get_files_from_corpus(self): 
		return 












