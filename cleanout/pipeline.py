# Import packages 
import nltk

# Import modules
from corpus import *
import utils
from extraff import extract_semantics, extract_from_corpus

# update wordnet if needed
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

