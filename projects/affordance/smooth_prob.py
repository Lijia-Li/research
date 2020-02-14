from collections import defaultdict, Counter
from os.path import dirname, realpath, join as join_path
import math

ROOT_DIRECTORY = dirname(dirname(dirname(realpath(__file__))))
stats_dir = join_path(ROOT_DIRECTORY, "data/output/smooth_test")  # todo: change this 

def read_counts(filename, reverse=0):
    dict_counter = defaultdict(Counter);
    cond = None;
    with open(filename, "r", encoding='utf-8') as f: 
        # create defaultdict in {condition: {variable: count}} format
        for i, line in enumerate(f): 
            items = line.split()
            num = int(items[1].strip("()"))
            # when the line is a condition
            if items[0][0:3] != "---":
                cond = items[0].strip("-")
                # dict_counter[cond] = Counter({cond: num})
            # when the line is variable
            elif items[0][0:3] == "---":
                var = items[0].strip("-")
                if reverse:
                	dict_counter[var].update({cond: num})
                else:
                	dict_counter[cond].update({var: num})
            else:
                print("%d line is a weird line %s" % (i, line))
            assert cond != None
    return dict_counter


def read_pair(filename):
	with open(filename, "r", encoding='utf-8') as f: 
		for i, line in enumerate(f): 
			adj, verb = line.split()
			yield [adj.strip("-"), verb.strip("-")]


def calculate():
	dict_n_a = read_counts(join_path(stats_dir, "count_noun_adj.txt"))
	dict_v_n = read_counts(join_path(stats_dir, "count_verb_noun.txt"))
	dict_n_v = read_counts(join_path(stats_dir, "count_verb_noun.txt"), reverse=1)
	print("finish reading dictionaries")

	# the total verbs in the corpus
	total_v = sum([sum(dict_n_v[verb].values()) for verb in dict_n_v.keys()])

	i = 0 
	# For each adj, verb pair
	for adj, verb in read_pair(join_path(stats_dir, "verb_adj_pair.txt")):
		if adj in ["'s", "-PRON-"]:
			continue
		prob_ls = []
		# for each noun that pair up with  
		for noun in list(dict_n_v[verb]): 
			# Calculate P(noun|adj)
			try: 
				p_n_a = dict_n_a[adj][noun] / sum(dict_n_a[adj].values())
			except ZeroDivisionError:
				print("zero devision",adj, verb)
				continue
			# Calculate P(verb|noun)
			p_v_n = dict_v_n[noun][verb] / sum(dict_v_n[noun].values())
			# Calculate P(V)
			p_v = float(sum(dict_n_v[verb].values()) / total_v)
			assert p_v != 0, "P(%s) here is zero" % verb
			# Calculating the conditional probability of P(verb|adj) / P(V)
			prob_ls.append(p_n_a * p_v_n / p_v)
		# sum up over all nouns
		p_v_a = sum(prob_ls)
		if p_v_a == 0: 
			print("p_v_a of {:s} {:s} is zero with list {:s}".format(adj, verb, str(prob_ls)))
			continue
		# write out to the files
		with open(join_path(stats_dir, "prob_v_adj_smooth.txt"), "a", encoding='utf-8') as f: 
			f.write('{:s} {:s} {:f} {:f}\n'.format(adj, verb, p_v_a, math.log(p_v_a)))


if __name__ == '__main__':
	calculate()



