from functools import reduce
import re

def nonempty_union(x, y):
    try:
        z = frozenset(x) | frozenset(y)
    except:
        z = x + y
    return list(filter(None, z)) if len(z) > 1 else list(z)

def vocabulary(string):
    try:
        string = string.replace(' ', '')
        components = [s.split(',') for s in string.split('|')]
        return list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components)))
    except AttributeError:
        return list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), string)))

def superpose(string_a, string_b, vocab_a = None, vocab_b = None):
    if vocab_a is None and vocab_b is None:
        string_a = string_a.replace(' ', '')
        string_b = string_b.replace(' ', '')
        components_b = [s.split(',') for s in string_b.split('|')]
        components_a = [s.split(',') for s in string_a.split('|')]
        vocab_a = list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components_a)))
        vocab_b = list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components_b)))
        return ['|'.join([','.join(s) for s in string_r]) for string_r in superpose(components_a, components_b, vocab_a, vocab_b)]

    if not string_a and not string_b:
        return [[]]
    if not string_a or not string_b:
        return []

    if frozenset(vocab_a) & frozenset(string_b[0]) <= frozenset(string_a[0]) and frozenset(vocab_b) & frozenset(string_a[0]) <= frozenset(string_b[0]):
        head_union = nonempty_union(string_a[0], string_b[0])
        l = L(string_a[0], string_a[1:], vocab_a, string_b[0], string_b[1:], vocab_b)
        return [[head_union] + l_item for l_item in l]

    return []

def L(head_a, tail_a, vocab_a, head_b, tail_b, vocab_b):
    part_1 = superpose([head_a] + tail_a, tail_b, vocab_a, vocab_b)
    part_2 = superpose(tail_a, [head_b] + tail_b, vocab_a, vocab_b)
    part_3 = superpose(tail_a, tail_b, vocab_a, vocab_b)
    return nonempty_union(nonempty_union(part_1, part_2), part_3)


def superpose_all(list_of_strings):
    if type(list_of_strings) != list:
        raise TypeError
    elif len(list_of_strings) == 0:
        raise Exception('Cannot use empty list')
    elif len(list_of_strings) == 1:
        return list_of_strings
    else:
        results = []
        for sp in superpose(list_of_strings[0], list_of_strings[1]):
            results += superpose_all([sp] + list_of_strings[2:])
        return results

import itertools
zipl = itertools.zip_longest

def pw_sp(string_a, string_b, vocab_a = None, vocab_b = None):
    "pointwise superposition"
    # Note: I'm assuming the shape of the data and not setting guards right now
    # May fix later if this becomes more prominently used
    components_a = string_a.replace(' ', '').split('|')
    components_b = string_b.replace(' ', '').split('|')
    res = []
    # slice off first and last elements (as these are always empty)
    for i, c in enumerate(components_a[1:-1]):
        for f in c.split(','):
            for j, d in enumerate(components_b[1:-1]):
                if f in d.split(','):
                    if len(res) == 0 or (res[-1][1] - res[-1][0]  == j - i):
                        # add one to account for sliced off elements
                        res.append((i+1, j+1))
                    else:
                        #  print('\033[31mProblem Strings: \033[36m', string_a, '&', string_b, '\033[0m')
                        return []
    if len(res) == 0:
        return []
    else:
        diff = res[0][1] - res[0][0]
    pad_a = components_a
    pad_b = components_b
    if diff > 0:
        for i in range(diff):
            pad_a = [''] + pad_a
            pad_b = pad_b + ['']
    elif diff < 0:
        for i in range(-diff):
            pad_a = pad_a + ['']
            pad_b = [''] + pad_b
    else:
        pass
    return [re.sub(r'\|+', '|', '|'.join([','.join(sorted(nonempty_union(x.split(','), y.split(',')))) for x, y in zipl(pad_a, pad_b, fillvalue='')]))]
