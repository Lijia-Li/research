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

# extract_from_corpus ("")s


# sentence = "John uses a knife to cut a red apple"
# doc = NLP(sentence)
# ss = extract_semantics(doc, rules)
# for s in ss: 
# 	# print(s["NOUN"])
# 	print(corpus.fill_empty_semantics(s))

# sentences =[ "John uses a knife to cut a red apple", 
# 			 "John uses a knife to cut a red apple"]
# for sentence in sentences:
# 	doc = NLP(sentence)
# 	ss = extract_semantics(doc, rules)
# 	for s in ss: 
# 	# print(s["NOUN"])
# 		print(s._src_dict)
# 	corpus.update_sql_count(ss)

# ls = [file for file in test_corpus.get_files_from_corpus()]
# assert str(ls) == "['data/test_corpus/5446419.txt', 'data/test_corpus/5460346.txt', 'data/test_corpus/5471936.txt']"
