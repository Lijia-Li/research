# Clean Up 

# Importing 
import spacy
import nltk
from nltk.corpus import wordnet as wn
from collections import namedtuple 
from extraff import *

SPACY_MODEL = 'en_core_web_sm'
try:
    NLP = spacy.load(SPACY_MODEL)
except OSError:
    spacy.cli.download(SPACY_MODEL)
    NLP = spacy.load(SPACY_MODEL)

# Corpus Class
# 	1. Corpus Folder Path
#	2. Cached txt Folder Path (tokenized)
# 	3. Prob files path 
# 	4. hook up SQL file




# Training Pipeline 
#	1.  Extract from corpus (verb, prep, subj, obj)
		# Cached as txt files (see file session)
# 	2. 	Count corpus words with coocurance 
		# Cached as ? file  (see file session)
# 	3. 	Calculate probability 
		# P(Adj | Noun) 
		# P(Verb | Noun)
		# P(Verb | Adj)
def extract_from_corpus (dump_dir): 
	# loop through each file in the directory
	for file in get_filename_from_folder(dump_dir):
		# loop through each sentence in the file
		semantics = []
		for sentence in get_sentence_from_file(dump_dir, file):
			semantics.extend(extract_semantics(doc))
		# prepare two list to output
		[S_list, NP_list] = prepare_semantics_for_output(semantics)
		# cache the list 
		print(S_list)
		print(NP_list)
		# add to SQLITE file


def prepare_semantics_for_output(semantics):
    S_ls = []
    NP_ls = []
    # semantics is list of dictionaries
    for semantic in semantics: 
        # if the dictionary is regarding the noun
        if "NOUN" in semantic.keys():
            NP_ls.append(semantic)
        else: 
            S_ls.append(semantic)
    return [NP_ls, S_ls]
            

def main():
	sentences = [
	    'The knife cut through the rancid meat like hot butter.',
	    'She used the knife to free herself, and she cut herself in the process.',
	]
	# only testing using sentence 1
	doc = NLP(sentences[0])
	semantics = extract_semantics(doc)
	assert str(extract_semantics(doc)) == "[{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}, {'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}]"
	assert str(prepare_semantics_for_output(semantics)) == "[[{'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}], [{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}]]"

	ROOT_DIRECTORY = dirname(dirname(dirname(realpath(__file__))))
	dump_dir = join_path(ROOT_DIRECTORY, "data/temp_test/dump")


	extract_from_corpus ("")


	print("here")

if __name__ == '__main__':
    main()





# [{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}, {'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}]
# [{'NOUN': meat, 'ADJ': rancid}, {'NOUN': butter, 'ADJ': hot}]
# [{'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife}]



# Testing Pipeline 
# 	0. check all the files in place
#	1. Extract manipulable noun form corpus
# 	2. ...


# File Session
# 	1. 	Extracted words file
# 		1.1 for each sentence in a file, extract (verb, prep, subj, obj)
# 		1.2 check criteria
# 		1.3 then store the output in a line 
# 		e.g. Sentence: The knife cut through the rancid meat like hot butter.
# 			 vpfile stores: "'VERB': cut, 'PREP': through, 'OBJ': meat, 'SUB': knife\n"
#			 npfile stores: "'NOUN': meat, 'ADJ': rancid\n" & "'NOUN': butter, 'ADJ': hot\n"	
#		or better: 
# 			 vpfile stores: "cut(VERB) through(PREP) meat(OBJ) knife(SUB)\n"
#			 npfile stores: "meat(NOUN) rancid(ADJ)\n" & "butter(NOUN) hot(ADJ)\n"	
# 		Q: do we still aim to check the noun is manipulable? if so, what about sub? 
#		   are we expecting subj and obj having different adj? if so, should we store seperatly?
# 	2. 	SQLITE count file
#		choice 1: 
# 			VERB 	PREP 	OBJ 	SUBJ 	COOCUR
# 	 		cut 	through meat 	knife 	1
#		choice 2: (relative database) 
#			VERB 	PREP 		VERB_ID		Noun_ID		meat_obj	knife_subj	
#			cut 	through								1			1
#			slice										1			
#			CON: from verb will work, but would the noun count can only be specific to one verb set. 
# 	3. SQLITE prob file
#		1.1 P(Adj | Noun) 
#		1.2 P(Verb | Noun)
#		1.3 P(Verb | Adj)
# 		1.4 






