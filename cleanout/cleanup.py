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

def extract_from_corpus(corpus, rules): 
	"""extract semantics from corpus, cache semantics, put them in to SQL count file (TODO)
	
	Arguments:
		corpus {Corpus} -- instance of Corpus class
		rules {dict{dict}} -- dictionary of rules TODO
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

		# save to SQL counts file (TODO)
		corpus.update_sql_count(semantics)
		
	return 

           

def main():
	# Create test corpus 
	dump_dir = "data/test_corpus";
	test_corpus = Corpus(dump_dir)

	# Create Rules for the extraff
	# TODO: Read RULES from a file in the corpus.
	rules = {
	    '': (
	        '((conj [VERB] (dobj [OBJ])))',
	    ),
	    'VERB': (
	        '([VERB] (prep [PREP] (pobj [OBJ])) (nsubj [SUB]))',
	        '([VERB] (nsubj [SUB]))',
	        '("use" (dobj [TOOL]) (xcomp [VERB] (dobj [OBJ])))',
	    ),
	    'NOUN': (
	        '([NOUN] (amod [ADJ]))',
	    ),
	}
	extract_from_corpus (test_corpus, rules)



if __name__ == '__main__':
    main()



# TODO: 
	# 2. add Lemmatizer in Extraff
	# 3. Calculate prob via SQL.
	# TODO: How to write pipeline.

# from ast import literal_eval
# literal_eval("{'noun': 'verb', 'adj': 'nice'}")


