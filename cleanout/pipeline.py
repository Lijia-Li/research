# Import packages 
import spacy
import nltk
from nltk.corpus import wordnet as wn
from collections import namedtuple 

# Import modules
from corpus import *
import utils
from extraff import extract_semantics

# Loading the tokenizer from spacy 
SPACY_MODEL = 'en_core_web_sm'
try:
    NLP = spacy.load(SPACY_MODEL)
except OSError:
    spacy.cli.download(SPACY_MODEL)
    NLP = spacy.load(SPACY_MODEL)

# get NLTK from wordnet 
nltk.download('wordnet', quiet=True)


def pipeline(corpus, rules):
	""" Pipeline for extracting a corpus, and calculate probabilities
	
		1. Extract from corpus (NP and VP)
			-> Cached as txt files
		2. Count corpus words with coocurance 
			-> Cached as sqlite database 
		3. Calculate probability
			-> P(verb|adj)
	
	Arguments:
		corpus {[Corpus]} -- a instance of corpus class, which is a wrapper around corpus documents
		rules {[dict]} -- rules that the corpus is parsed with
	"""
	
	# Extract corpus to counts SQLite
	extract_from_corpus (corpus, rules)

	# generate 
	corpus.v_a_pair()
	corpus.cal_prob_v_a()


def extract_from_corpus(corpus, rules): 
	"""extract semantics from corpus, cache semantics, put them in to SQL count file
	
	Arguments:
		corpus {Corpus} -- instance of Corpus class
		rules {dict{dict}} -- dictionary of rules
	"""
	# loop through each file in the directory

	for file in corpus.get_files_from_corpus():
		semantics = []
		# loop through each sentence in the file
		for sentence in get_sentence_from_file(file): 
			# tokenize sentence
			doc = NLP(sentence)
			# extract semantics from the document with specified rules
			semantics.extend(extract_semantics(doc, rules))
		
		# cache semantic dictionary, to avoid parsing again
		corpus.cache_semantic_dict(semantics, file)

		# save to SQL counts file
		corpus.update_sql_count(semantics)
		print("Finished processing file {}".format(file))
		
	return corpus
      

def main():
	# Create test corpus 
	test_corpus = Corpus("data/test_corpus")
	small_corpus = Corpus("data/small_corpus")

	# Read rules
	rules = get_rules("./rules.txt")

	# Run extraction & prob calculation
	pipeline(test_corpus, rules)


if __name__ == '__main__':
    main()

