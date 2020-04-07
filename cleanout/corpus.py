# Corpus Class
# 	1. Corpus Folder Path
#	2. Cached txt Folder Path (tokenized)
# 	3. Prob files path 
# 	4. hook up SQL file


# FOLDER LAYOUT
# dump 
# |----corpus
# |----processed_corpus
#		 |---- NP
#		 |---- VP
# |----stats
# 		 |---- np_count.db
# 		 |---- vp_count.db
# 		 |---- cashed_prob/
#		 |---- sql_prob/

import sys
from os import mkdir, listdir, path
from os.path import exists as file_exists, join as join_path, dirname, realpath

import sqlite3

from utils import *


class Corpus:
	"""a class to wrap around corpus, including corpus and their data"""
	def __init__(self, dump_dir):
		self.dump_dir = dump_dir

		self.corpus_dir = join_path(self.dump_dir, "corpus")
		self.stats_dir = join_path(self.dump_dir, "stats")

		self.NP_extract_dir = join_path(self.dump_dir, "processed_corpus/NP")  # pylint: disable=invalid-name
		self.VP_extract_dir = join_path(self.dump_dir, "processed_corpus/VP")  # pylint: disable=invalid-name
		
		self.np_count_path = join_path(self.stats_dir, "np_count.db")
		self.vp_count_path = join_path(self.stats_dir, "vp_count.db")

		self.cashed_prob = join_path(self.stats_dir, "cashed_prob")
		self.sql_prob = join_path(self.stats_dir, "sql_prob")
    
	@property
	def np_conn(self): 
		"""noun phrase database connection
		
		Returns:
			db connection -- the connection to noun phrase count database
		"""
		# if db already created
		if path.exists(self.np_count_path): 
			conn = sqlite3.connect(self.np_count_path)
			c = conn.cursor()

		# otherwise, construct the db
		else: 
			conn = sqlite3.connect(self.np_count_path)
			c = conn.cursor()
			# Create a table with the column names
			c.execute("""CREATE TABLE NP(
						np_id INTEGER PRIMARY KEY AUTOINCREMENT,
						noun TEXT,
						adj TEXT,
						cooccur INTEGER DEFAULT 1
						)""")
		return conn

	@property
	def vp_conn(self): 
		"""verb phrase database connection
		
		Returns:
			db connection -- the connection to verb phrase count database
		"""
		# if db already created
		if path.exists(self.vp_count_path): 
			conn = sqlite3.connect(self.vp_count_path)
			c = conn.cursor()

		# otherwise, construct the db
		else: 
			conn = sqlite3.connect(self.vp_count_path)
			c = conn.cursor()
			# Create a table with the column names
			c.execute("""CREATE TABLE VP(
						vp_id INTEGER PRIMARY KEY AUTOINCREMENT,
						verb TEXT,
						prep TEXT,
						subj TEXT, 
						obj TEXT,
						cooccur INTEGER DEFAULT 1
						)""")
		return conn


	def get_files_from_corpus(self): 
		"""yield path + filename for reading processing
		
		Yields:
			str -- "path/filename" 
		"""
		return get_filelist_from_folder(self.corpus_dir)


	def cache_semantic_dict(self, semantics, file):
		"""cache out the semantics to processed_corpus folder

		Arguments:
			s_dict {dict(dict(semantic))} TODO
			file {str} -- path name of the origonal file
			type {str} -- "NP" or "VP"
		
		Raises:
			KeyError -- [when the type is maldefined]
		"""
		# Prepare two file path
		file_id = file.split("/")[-1]
		vp_path = "{}/{}".format(self.VP_extract_dir, file_id)
		np_path = "{}/{}".format(self.NP_extract_dir, file_id)

		with open(vp_path, "w", encoding='utf-8') as f_v, \
			 open(np_path, "w", encoding='utf-8') as f_n: 

			# Identify if the semantic is VP or NP, and cache to according file
			for semantic in semantics: 
				if "NOUN" in semantic.keys():
					f_n.write(str(semantic._src_dict) + "\n")
				else: 
					f_v.write(str(semantic._src_dict) + "\n")
		return


	def update_sql_count(self, semantics):
		np_semantics = []
		vp_semantics = []

		for semantic in semantics: 
			if "NOUN" in semantic.keys():
				np_semantics.append(semantic)
			else: 
				vp_semantics.append(semantic)

		self.update_np_count(np_semantics)
		self.update_vp_count(vp_semantics)

		return 


	def update_np_count(self, semantics):
		"""Update NP count SQL with NP_list
		
		Arguments:
			semantics  {list(dict())} -- e.g. [{'NOUN': 'apple', 'ADJ': 'red'}]
		"""
		# conn = sqlite3.connect(self.np_count_path)
		conn = self.np_conn;
		c = conn.cursor()

		# update or insert semantic into the sqlite
		for semantic in semantics:
			# Check if the semantic already exist or not			
			c.execute('''
				        SELECT np_id FROM NP WHERE noun=? AND adj=?
			    	''', (semantic['NOUN'], semantic['ADJ']))
			temp = c.fetchall()

			# If not exist, insert
			if len(temp) == 0:
				c.execute('''INSERT INTO NP (noun, adj) VALUES (?, ?)
							''', (semantic['NOUN'], semantic['ADJ']))
			# If already exist, update the cooccurance. 
			else:
				c.execute(''' UPDATE NP SET cooccur = cooccur + 1 WHERE noun=? AND adj=?
							''', (semantic['NOUN'], semantic['ADJ']))
			conn.commit()

		# c.execute("SELECT * FROM NP")
		# print(c.fetchall())
		
		conn.close()

		return


	def update_vp_count(self, semantics):
		"""Update VP sqlite count with semantics list
		
		Arguments:
			semantics {list(dict())} -- e.g. [{'TOOL': 'knife', 'VERB': 'cut', 'OBJ': 'apple'}]
		"""

		# connect to the database 
		conn = self.vp_conn;
		c = conn.cursor()

		# update or insert semantic into the sqlite
		for semantic in semantics:
			semantic = self.fill_empty_semantics(semantic)
			# Check if the semantic already exist or not			
			c.execute('''
				        SELECT vp_id FROM VP 
				        WHERE verb=? AND prep=? AND subj=? AND obj=?
			    		''', (semantic['VERB'], semantic['PREP'], semantic['SUB'], semantic['OBJ']))
			temp = c.fetchall()

			# If not exist, insert
			if len(temp) == 0:
				c.execute('''
							INSERT INTO VP (verb, prep, subj, obj) VALUES (?, ?, ?, ?)
							''', (semantic['VERB'], semantic['PREP'], semantic['SUB'], semantic['OBJ']))
			# If already exist, update the cooccurance. 
			else:
				c.execute(''' 
							UPDATE VP SET cooccur = cooccur + 1 
							WHERE verb=? AND prep=? AND subj=? AND obj=?
							''', (semantic['VERB'], semantic['PREP'], semantic['SUB'], semantic['OBJ']))
			conn.commit()

		# c.execute("SELECT * FROM VP")
		# print(c.fetchall())
		
		conn.close()

		return


	def fill_empty_semantics(self, semantics): 
		"""fill the semantics dictionary with None for empty parameters, to prepare for insert into SQLite
		
		
		Arguments:
			semantics {list(dict())} -- e.g. [{'TOOL': 'knife', 'VERB': 'cut', 'OBJ': 'apple'}]
		
		Returns:
			[type] -- [description]
		"""
		fields = ['VERB', 'PREP', 'SUB', 'OBJ']
		semantics = semantics._src_dict
		for field in fields: 
			try: 
				semantics[field]
			except KeyError:
				semantics[field] = ""
		return semantics












