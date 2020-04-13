"""A file that contains functions aim to extracting semantics"""
import spacy
from nltk.corpus import wordnet as wn
from utils import censor

# Loading the tokenizer from spacy 
SPACY_MODEL = 'en_core_web_sm'
try:
    NLP = spacy.load(SPACY_MODEL)
except OSError:
    spacy.cli.download(SPACY_MODEL)
    NLP = spacy.load(SPACY_MODEL)

class FrozenDict:

    def __init__(self, src_dict):
        self._src_dict = src_dict
        self._hash = hash(tuple(
            (key, value) for key, value in self._src_dict.items()
        ))

    def __len__(self):
        return len(self._src_dict)

    def __contains__(self, key):
        return key in self._src_dict

    def __getitem__(self, key):
        return self._src_dict[key]

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._src_dict == other
        elif isinstance(other, FrozenDict):
            return self._src_dict == other._src_dict
        else:
            return False

    def __hash__(self):
        return self._hash

    def keys(self):
        return self._src_dict.keys()

    def values(self):
        return self._src_dict.values()

    def items(self):
        return self._src_dict.items()


def match_tree(token, rule):

    def _match_tree(token, rule, result):
        paren_count = 0
        index = 0
        # make sure the rule is balanced with paranthesis
        for index, char in enumerate(rule):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
        rule = rule[:index + 1]
        index = 1

        while index < len(rule):
            word = rule[index:rule.find(' ', index)]
            if word.startswith('-'):
                pass
            elif word.startswith('"') and word.endswith('"'):
                stem = word[1:-1]
                if wn.morphy(token.text) != stem:
                    return len(rule), None
                index = index + len(word) + 1
            elif word.startswith('[') and word.endswith(']'):
                # update the matched result dictionaty
                result[word[1:-1]] = censor(token)
                index = index + len(word) + 1
            elif word.startswith('('):
                prev_index = index
                for child in token.children:
                    if child.dep_ == word[1:]:
                        span = _match_tree(child, rule[index:-1], result)
                        index += span
                if prev_index == index:
                    result.clear()
                    return len(rule)
            else:
                index += len(word) + 1
        return len(rule)

    result = {}
    _match_tree(token, rule, result)
    return FrozenDict(result)


def print_parse_tree(doc, prefix=''):

    def print_token_tree(token, depth=0):
        print(f'{prefix}{depth * "  "} {token.dep_}: {token} ({token.pos_})')
        for child in token.children:
            print_token_tree(child, depth + 1)

    for token in doc:
        if token.dep_ == 'ROOT':
            print_token_tree(token)
            break
    return


def extract_semantics(doc, RULES):
    """extract semantics by matching the tokens to the given rules
    
    Arguments:
        doc {list} -- list of tokens
        RULES {dict(tuple)} -- dictionary of rules, {root: (rule, rule)}
                            -- example can be found in ./rules.txt
    
    Returns:
        [type] -- [description]
    """
    semantics = []

    for token in doc:
        # for each set of rule that have different roots
        for rules in (RULES.get(''), RULES.get(token.pos_, [])):
            max_length = 0
            rule_semantics = []
            # match every rule of the same root
            for rule in rules:
                match = match_tree(token, rule)
                # preserve match that are the same or longer than max match
                if match:
                    if len(match) > max_length:
                        rule_semantics = [match]
                        max_length = len(match)
                    elif len(match) == max_length:
                        rule_semantics.append(match)
            # add to the return list
            semantics.extend(rule_semantics)
    return semantics


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


if __name__ == '__main__':
    benchmark()
