
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
                    actual = extract_semantics(doc)
                    if actual != extractions:
                        print_failed(doc, actual, extractions)
                        incorrect += 1
                    count += 1
                sentence = line.strip()
                extractions = set()
    print(f'Score: {count - incorrect} / {count}')


