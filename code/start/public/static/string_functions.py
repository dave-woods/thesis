from functools import reduce
from collections import Counter
import itertools
import re

# ['r','g','b']
# -> ['r|b|g', 'r|g|b', 'b|r|g', 'b|g|r', 'g|r|b', 'g|b|r']
def permute(items):
    return ['|'.join(i) for i in itertools.permutations(items)]

def border_box_variants(string):
    components = get_components(string)
    return ['{}|{}'.format(negate_component(components[0], True), string), '{}|{}'.format(string, negate_component(components[-1], True)), '{}|{}|{}'.format(negate_component(components[0], True), string, negate_component(components[-1], True))]

def negate_component(component, as_string=False):
    c = list(map(lambda f: f[1:] if f == '' or f.startswith('!') else '!'+f, component))
    return c if not as_string else ','.join(c)

def negate_string(string):
    return '|'.join([','.join(c) for c in map(negate_component, get_components(string))])

def hide_negated(string):
    newc = []
    for c in get_components(string):
        newc.append(list(filter(lambda f: not f.startswith('!'), c)))
    return '|'.join([','.join(c) for c in newc])

def nonempty_union(x, y):
    try:
        z = frozenset(x) | frozenset(y)
    except:
        z = x + y
    return list(filter(None, z)) if len(z) > 1 else list(z)

def get_components(string):
    return [s.split(',') for s in string.replace(' ', '').split('|')]

def vocabulary(string):
    try:
        components = get_components(string)
        return list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components)))
    except AttributeError:
        return list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), string)))

def string_length(string):
    return len(string.split('|'))

def reduct(string, new_vocab):
    components = get_components(string)
    reducted = [[f for f in c if f in new_vocab] for c in components]
    return '|'.join([','.join(c) for c in reducted])

def block_compress(string):
    components = get_components(string)
    if len(components) < 2:
        return '|'.join([','.join(c) for c in components])
    elif Counter(components[0]) == Counter(components[1]):
        return block_compress('|'.join([','.join(c) for c in components[1:]]))
    else:
        return ','.join(components[0]) + '|' + block_compress('|'.join([','.join(c) for c in components[1:]]))

def delete_empty_boxes(string):
    components = get_components(string)
    return '|'.join([','.join(c) for c in components if c not in [[], ['']]])

# can this also be made into a generator?? I think so
def superpose(string_a, string_b, vocab_a = None, vocab_b = None):
    if vocab_a is None and vocab_b is None:
        components_a = get_components(string_a)
        components_b = get_components(string_b)
        vocab_a = list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components_a)))
        vocab_b = list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components_b)))
        splist = ['|'.join([','.join(s) for s in string_r]) for string_r in superpose(components_a, components_b, vocab_a, vocab_b)]
        return splist

    if not string_a and not string_b:
        return [[]]
    if not string_a or not string_b:
        return []

    # first one was old version, not sure if new one is technically correct or not, but gives better results
    if frozenset(vocab_a) & frozenset(string_b[0]) <= frozenset(string_a[0]) and frozenset(vocab_b) & frozenset(string_a[0]) <= frozenset(string_b[0]):
    # if frozenset(vocab_a) & frozenset([x for x in string_b[0] if not x.startswith('!')]) <= frozenset([x for x in string_a[0] if not x.startswith('!')]) and frozenset(vocab_b) & frozenset([x for x in string_a[0] if not x.startswith('!')]) <= frozenset([x for x in string_b[0] if not x.startswith('!')]):
        head_union = nonempty_union(string_a[0], string_b[0])
        
        # removes '|a|b| & |!a|b|' cases
        for zz in head_union:
            if zz.startswith('!') and zz[1:] in head_union:
                return []
        
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
        yield list_of_strings[0]
    else:
        for sp in superpose(list_of_strings[0], list_of_strings[1]):
            yield from superpose_all([sp] + list_of_strings[2:])

def superpose_langs(lang1, lang2):
    for s1 in lang1:
        for s2 in lang2:
            yield from superpose(s1, s2)

def superpose_all_langs(list_of_langs, filt=None):
    return reduce(lambda x,y: [s for s in superpose_langs(x,y) if filt is None or filt(s)], list_of_langs)

def superpose_all_langs_gen(list_of_langs, filt=None):
    running = list_of_langs[0]
    for lang in list_of_langs[1:]:
        yield running
        running = [s for s in superpose_langs(running, lang) if filt is None or filt(s)]
    yield running

def superpose_all_langs_pick_shortest(list_of_langs, filt=None):
    # print('new cond')
    # print(list_of_langs)
    # input('[Hit enter to continue]')
    if len(list_of_langs) == 1:
        return list_of_langs[0]
    list_of_langs.sort(key=lambda l: len(l))
    shortest = list_of_langs[0]
    checks = []
    idx = 1
    for lang in list_of_langs[1:]:
        checks.append((idx, [s for s in superpose_langs(shortest, lang) if filt is None or filt(s)]))
        idx += 1
    checks_filt = [c for c in checks if len(c[1]) > 0]
    checks_filt.sort(key=lambda l: len(l[1]))
    try:
        shortest = checks_filt[0]
        ll = [shortest[1]] + list_of_langs[1:shortest[0]] + list_of_langs[shortest[0]+1:]
        return superpose_all_langs_pick_shortest(ll, filt)
    except IndexError:
        pass
        # for l in list_of_langs:
        #     print([hide_negated(s) for s in l])
        # print('---')
        # print(checks)

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
