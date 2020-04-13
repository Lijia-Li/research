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
		self.p_v_a_path = join_path(self.stats_dir, "p_v_a.db")

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

	@property
	def p_v_a_conn(self):
		# if db already created
		if path.exists(self.p_v_a_path): 
			conn = sqlite3.connect(self.p_v_a_path)

		# otherwise, construct the db
		else: 
			# create table
			conn = sqlite3.connect(self.p_v_a_path)
			c = conn.cursor()
			# Create a table with the column names
			c.execute("""CREATE TABLE PVA(
						va_id INTEGER PRIMARY KEY AUTOINCREMENT,
						verb TEXT,
						adj TEXT,
						prob INTEGER DEFAULT -1
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
			s_dict {dict(dict(semantic))} ”
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
		"""A wrapper function to call both update_np_count and update_vp_count"""
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

	# Calculate P(verb|adj)
	# Calculate P(verb|adj) | P(verb)
	# Note only considering subj
	def cal_prob_v_a(self): 
		"""Calculate P(verb|adj) = P(verb|noun) * P(noun|adj)"""

		# connecting databases
		vdb = self.vp_conn.cursor()
		ndb = self.np_conn.cursor()
		conn = self.p_v_a_conn
		pva_db = conn.cursor()

		# obtain pairs from the database
		pva_db.execute("SELECT verb, adj FROM PVA")
		v_a_pair = pva_db.fetchall()

		# for each pari, calculate P(verb|adj) = P(verb|noun) * P(noun|adj) (for all nouns) 
		for verb, adj in v_a_pair:
			# list of P(V|N1) * P(N1|adj), where each prob is for a N1 
			prob_ls = [] 

			# get adj base count
			ndb.execute("SELECT adj, SUM(cooccur) FROM NP WHERE adj=?", (adj,))
			a_count = ndb.fetchall()[0][1]
			# print(a_count)

			# obtain list of subj, which describe noun which afford verb
			vdb.execute("SELECT subj FROM VP WHERE verb=?", (verb,))
			subj_ls = [s[0] for s in vdb.fetchall()]

			# loop through all the subj, where a subj is called N1 in the comment
			for subj in subj_ls: 

				# obtain adj cooccurance with N1
				ndb.execute("SELECT adj, noun, SUM(cooccur) FROM NP WHERE adj=? AND noun=?", (adj, subj))
				a_n_count = ndb.fetchall()[0][2]
				
				# if N1 and adj does not cooccur, move on to the next N1
				if a_n_count is None: 
					continue
				# print(a_n_count)

				# calculate P(N1|adj)
				p_n_a = a_n_count / a_count
				# print("A|N: P({}|{}) = {}".format(subj, adj, p_n_a))

				# obtain N1 appeared times total
				vdb.execute("SELECT subj, SUM(cooccur) FROM VP WHERE subj=?", (subj,))
				n_count = vdb.fetchall()[0][1]
				# print("{}(NOUN) occur {} times in the file".format(subj, n_count))

				# obtain verb, N1 cooccurance
				vdb.execute("SELECT verb, subj, SUM(cooccur) FROM VP WHERE verb=? AND subj=?", (verb, subj))
				v_n_count = vdb.fetchall()[0][2]
				# print("{}(VERB) and {}(NOUN) coocur {} times".format(verb, subj, v_n_count))

				# calculate P(verb|N1)
				p_v_n = v_n_count / n_count
				# print("V|S: P({}|{}) = {}".format(verb, subj, p_v_n))

				# append the P(V|N1) * P(N1|adj) to prob list
				prob_ls.append(p_v_n * p_n_a)
				# print("appending {} to prob list".format(p_v_n * p_n_a))

			# get sum of probability over all N1s --> P(verb|adj)
			print("P(verb|adj): P({}|{}) {}".format(verb, adj, sum(prob_ls)))
			pva_db.execute("UPDATE PVA SET prob=? WHERE verb=? AND adj=?", (sum(prob_ls), verb, adj))
			conn.commit()

		conn.close()
		return


	def v_a_pair(self):
		"""Obtain the verb adj pair to prepare calculating P(verb|adj)"""
		vdb = self.vp_conn.cursor()
		ndb = self.np_conn.cursor()
		conn = self.p_v_a_conn
		pva_db = conn.cursor()

		# obtain unique verbs in the sqlite
		vdb.execute("SELECT verb FROM VP")
		# [('cut',), ('lay',)] --> ['cut', 'lay']
		verb_ls = [v[0] for v in vdb.fetchall()] 
		verb_ls = list(set(verb_ls))

		# loop through all the
		for verb in verb_ls:
			# obtain list of subj
			vdb.execute("SELECT subj FROM VP WHERE verb=?", (verb,))
			subj_ls = [s[0] for s in vdb.fetchall()]
			subj_ls = list(set(subj_ls))

			for subj in subj_ls: 
				# obtain all the adjectives that describe the subj
				ndb.execute("SELECT adj FROM NP WHERE noun=?", (subj,))
				adj_ls = [adj[0] for adj in ndb.fetchall()]
				for adj in adj_ls:
					# print(verb, adj)
					pva_db.execute("INSERT INTO PVA(verb, adj) VALUES (?, ?)", (verb, adj))
				conn.commit()
		conn.close()

		return 


	def cal_prob_v_n(self, noun): 
		# P(verb|N1) = P(verb|adj) * P(adj|N1)
		p_v_n = {}
		# {verb1: [0.234, 0.12313]; verb2: [0.1]}

		pva_db = self.p_v_a_conn.cursor()
		ndb = self.np_conn.cursor()

		ndb.execute("SELECT noun, SUM(cooccur) FROM NP WHERE noun=?", (noun,))
		n_count = ndb.fetchall()[0][1]

		# obtain all the adj
		ndb.execute("SELECT adj, noun FROM NP WHERE noun=?", (noun,))
		adj_ls = [t[0] for t in ndb.fetchall()]

		for adj in adj_ls:
			# obtain adj cooccurance with noun
			ndb.execute("SELECT adj, noun, SUM(cooccur) FROM NP WHERE adj=? AND noun=?", (adj, noun))
			a_n_count = ndb.fetchall()[0][2]

			# P(adj|N1)
			p_a_n = a_n_count / n_count

			# Fetch all the verbs
			pva_db.execute("SELECT verb, adj, prob FROM PVA WHERE adj=?", (adj,))
			verb_ls = pva_db.fetchall()

			for verb, adj, p_v_a in verb_ls: 
				if p_v_n[verb]: 
					p_v_n[verb] = p_v_n[verb] + p_v_a * p_a_n
				else: 
					p_v_n[verb] = p_v_a * p_a_n

		return p_v_n






		




