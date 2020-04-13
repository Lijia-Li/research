import re
from ast import literal_eval

import spacy

from extraff import *
from utils import get_rules

# Loading the tokenizer from spacy 
SPACY_MODEL = 'en_core_web_sm'
try:
    NLP = spacy.load(SPACY_MODEL)
except OSError:
    spacy.cli.download(SPACY_MODEL)
    NLP = spacy.load(SPACY_MODEL)

def benchmark():
    def print_failed(doc, actual, expected):
        print(f'Failed sentence "{sentence}":')
        print(f'    expected:')
        for binding in extractions:
            print('        {'
                + ', '.join(f'{key}: {value}' for key, value in binding.items())
                + '}'
            )
        print(f'    actual:')
        for binding in actual:
            print('        {'
                + ', '.join(f'{key}: {value}' for key, value in binding.items())
                + '}'
            )
        print(f'    parse tree:')
        print_parse_tree(doc, prefix='        ')

    rules = get_rules("./rules.txt")
    count = 0
    incorrect = 0
    with open('benchmark') as fd:
        sentence = None
        extractions = set()
        for line in [*fd.read().splitlines(), '']:
            if line.startswith(' '):
                assert "'" not in line
                extractions.add(FrozenDict(literal_eval(
                    '{' + re.sub(r'(\w+)', r'"\1"', line) + '}'
                )))
            else:
                if sentence is not None:
                    doc = NLP(sentence)
                    actual = extract_semantics(doc, rules)
                    if actual != extractions:
                        print_failed(doc, actual, extractions)
                        incorrect += 1
                    count += 1
                sentence = line.strip()
                extractions = set()
    print(f'Score: {count - incorrect} / {count}')

if __name__ == "__main__":
    benchmark()
