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
# |----processed_corpus
#		 |---- NP
#		 |---- VP
# |----stats
# 		 |---- cashed_prob
#		 |---- sql_prob

import sys
from os import mkdir, listdir
from os.path import exists as file_exists, join as join_path, dirname, realpath

from utils import *

# sys.path.insert(0, ROOT_DIRECTORY)

class Corpus:
	"""a class to wrap around corpus, including corpus and their data"""
	def __init__(self, dump_dir):
		self.dump_dir = dump_dir

		self.corpus_dir = join_path(self.dump_dir, "corpus")
		self.stats_dir = join_path(self.dump_dir, "stats")

		self.NP_extract_dir = join_path(self.dump_dir, "processed_corpus/NP")  # pylint: disable=invalid-name
		self.VP_extract_dir = join_path(self.dump_dir, "processed_corpus/VP")  # pylint: disable=invalid-name
		
		self.cashed_prob = join_path(self.stats_dir, "cashed_prob")
		self.sql_prob = join_path(self.stats_dir, "sql_prob")
    

	def get_files_from_corpus(self): 
		return get_filelist_from_folder(self.corpus_dir)

	def cache_semantic_list(self, s_list, file, type):
		"""cache out the semantics to processed_corpus folder

		Arguments:
			s_list {list(list(semantic))} -- e.g. [[NOUN: school ADJ: high], 
[NOUN: place ADJ: tight]]
			file {str} -- path name of the origonal file
			type {str} -- "NP" or "VP"
		
		Raises:
			KeyError -- [when the type is maldefined]
		"""
		
		# Get the appropriate path 
		if type == "NP":
			path = join_path(self.NP_extract_dir, file.split("/")[-1])
		elif type == "VP": 
			path = join_path(self.VP_extract_dir, file.split("/")[-1])
		else: 
			raise KeyError("Only accept NP or VP")

		# Cache out the processed data
		with open(path, "w+", encoding='utf-8') as f:
			for s in s_list: 
				for item in s:
					f.write(item + " ") 
				f.write("\n")
		return


	def main():
		return



if __name__ == '__main__':
    main()




