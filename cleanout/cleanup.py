# Clean Up 

# Import packages 
import spacy
import nltk
from nltk.corpus import wordnet as wn
from collections import namedtuple 

# Import modules
from corpus import *
import utils
from extraff import extract_semantics

# Loading the tokenizer 
SPACY_MODEL = 'en_core_web_sm'
try:
    NLP = spacy.load(SPACY_MODEL)
except OSError:
    spacy.cli.download(SPACY_MODEL)
    NLP = spacy.load(SPACY_MODEL)


def pipeline(Corpus):
	extract_from_corpus(Corpus)


# Training Pipeline 
#	1.  Extract from corpus (verb, prep, subj, obj)
		# Cached as txt files (see file session)
# 	2. 	Count corpus words with coocurance 
		# Cached as ? file  (see file session)
# 	3. 	Calculate probability 
		# P(Adj | Noun) 
		# P(Verb | Noun)
		# P(Verb | Adj)

def extract_from_corpus(corpus): 
	"""extract semantics from corpus, cache semantics, put them in to SQL count file (TODO)
	
	Arguments:
		corpus {Corpus} -- instance of Corpus class
	"""
	# loop through each file in the directory
	for file in corpus.get_files_from_corpus():
		# loop through each sentence in the file
		semantics = []
		for sentence in get_sentence_from_file(file): 
			# tokenize sentence
			doc = NLP(sentence)
			semantics.extend(extract_semantics(doc))
		# prepare two list to output
		[VP_list, NP_list] = prepare_semantics_for_output(semantics)
		# cache the list 
		corpus.cache_semantic_list(VP_list, file, "VP")
		corpus.cache_semantic_list(NP_list, file, "NP")

		print(NP_list)
		# save to SQL counts file (TODO)
		corpus.update_NP_count(NP_list)

		# corpus.update_VP_count(VP_list)

	return 


def prepare_semantics_for_output(semantics):
	"""unpack FrozenDict to List for output
	
	Arguments:
		semantics {set(FrozenDict)} -- extracted semantics from a sentence
	Return:
		[VP_list, NP_list], where
		VP/NP_list {list(str)} -- e.g. ['NOUN: meat', 'ADJ: rancid']
	"""
	VP_list = []
	NP_list = []
	# semantics is list of dictionaries
	for semantic in semantics: 
		sem_ls = [f'{key}: {value}' for key, value in semantic.items()]
		# if the dictionary is regarding the noun
		if "NOUN" in semantic.keys():
			NP_list.append(sem_ls)
		else: 
			VP_list.append(sem_ls)
	return [VP_list, NP_list]
            

def main():
	# sentences = [
	#     'The knife cut through the rancid meat like hot butter.',
	#     'She used the knife to free herself, and she cut herself in the process.',
	# ]
	# # only testing using sentence 1
	# doc = NLP(sentences[0])
	# semantics = extract_semantics(doc)
	# prepare_semantics_for_output(semantics)
	# assert str(extract_semantics(doc)) == "[{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}, {'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}]"
	# assert str(prepare_semantics_for_output(semantics)) == "[[{'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}], [{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}]]"

	# ROOT_DIRECTORY = dirname(dirname(dirname(realpath(__file__))))
	# dump_dir = join_path(ROOT_DIRECTORY, "data/temp_test/dump")

	# extract_from_corpus ("")

	
	# Create test corpus 
	dump_dir = "data/test_corpus";
	test_corpus = Corpus(dump_dir)

	
	ls = [file for file in test_corpus.get_files_from_corpus()]
	# assert str(ls) == "['data/test_corpus/5446419.txt', 'data/test_corpus/5460346.txt', 'data/test_corpus/5471936.txt']"

	extract_from_corpus (test_corpus)



if __name__ == '__main__':
    main()



# TODO: 
	# 1. semantic -> count SQL file
	# 2. add Lemmatizer in Extraff
	# 3. Calculate prob via SQL.


