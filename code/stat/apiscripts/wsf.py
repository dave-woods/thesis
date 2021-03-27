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

def subsets(s):
    return frozenset(frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1)))

def proper_subsets(s):
    return frozenset(frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s))))

def nonempty_union(x, y):
    try:
        z = frozenset(x) | frozenset(y)
    except:
        z = x + y
    return list(filter(None, z)) if len(z) > 1 else list(z)

def get_components(string):
    try:
        return [s.split(',') for s in string.replace(' ', '').split('|')]
    except AttributeError:
        return string

def string_from_components(components):
    return '|'.join([','.join(c) for c in components])

def vocabulary(string):
    if string == '' or string == []:
        return frozenset()
    try:
        components = get_components(string)
        return frozenset(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components)))
    except AttributeError:
        return frozenset(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), string)))

def vocabulary_lang(lang):
    return frozenset(reduce(lambda x, y: list(vocabulary(x) | vocabulary(y)), lang, []))

def string_length(string):
    return len(string.split('|'))

def sort_fluents(string):
    return '|'.join([','.join(sorted(x.split(','))) for x in string.split('|')])

def string_equals(a, b):
    return [sorted(x.split(',')) for x in a.split('|')] == [sorted(x.split(',')) for x in b.split('|')]

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

def projection(string, proj_set):
    return block_compress(reduct(string, proj_set))

def projects_to(a, b):
    return string_equals(b, projection(a, vocabulary(b)))

def string_projects_to_string(a, b):
    return projects_to(a, b)

def lang_projects_to_string(a, b):
    return all([string_projects_to_string(s, b) for s in a])

def lang_projects_to_lang(a, b):
    return all([lang_projects_to_string(a, s) for s in b])

def lang_contains_string(a, b):
    return any([string_projects_to_string(s, b) for s in a])

def lang_contradicts_string(a, b):
    return not lang_contains_string(a,b) and any([vocabulary(s).issuperset(vocabulary(b)) for s in a])

def projection_lang(lang, new_vocab):
    return list(set(filter(lambda n: n != '', [projection(s, new_vocab) for s in lang])))

def projection_full_vocab(string, vocab):
    p = projection(string, vocab)
    return p if vocabulary(p) == frozenset(vocab) else ''

def projection_lang_full_vocab(lang, new_vocab):
    return list(set(filter(lambda n: n != '', [projection_full_vocab(s, new_vocab) for s in lang])))

def analogous_strings(a, b):
    v_a = vocabulary(a)
    v_b = vocabulary(b)
    mapping = dict()
    for v in v_a:
        for w in v_b.difference(frozenset(mapping.values())):
            if reduct(a, [v]) == reduct(b, [w]).replace(w, v):
                mapping[v] = w
                break
    return frozenset(mapping.keys()) == v_a and frozenset(mapping.values()) == v_b, mapping


def delete_empty_boxes(string):
    components = get_components(string)
    return '|'.join([','.join(c) for c in components if c not in [[], ['']]])

# returns a string
def basic_sp(string_a, string_b):
    components_a = get_components(string_a)
    components_b = get_components(string_b)
    return sort_fluents(string_from_components([nonempty_union(a, b) for (a, b) in zip(components_a, components_b)]))

# returns a language
def basic_sp_lang(lang_a, lang_b):
    result = []
    for a in lang_a:
        for b in lang_b:
            result.append(basic_sp(a, b))
    return frozenset(result)

# returns a language
def pad(string, length):
    sl = string_length(string)
    if length < sl:
        return []
    elif length == sl:
        return [string]
    else:
        result = []
        for s in pad(string, length-1):
            c = get_components(s)
            result = result + [string_from_components(c[:i] + [c[i]] + c[i:]) for i in range(len(c))]
        return frozenset(result)

# returns a language
def async_sp(string_a, string_b):
    len_a = string_length(string_a)
    len_b = string_length(string_b)
    pad_len = len_a + len_b - 1
    padded_a = pad(string_a, pad_len)
    padded_b = pad(string_b, pad_len)
    return frozenset(map(lambda s: block_compress(s), basic_sp_lang(padded_a, padded_b)))

# can this also be made into a generator?? I think so
# returns a language
def superpose(string_a, string_b, vocab_a = None, vocab_b = None, remove_negated_pairs = True):
    components_a = get_components(string_a)
    components_b = get_components(string_b)
    if vocab_a is None and vocab_b is None:
        vocab_a = vocabulary(string_a)
        vocab_b = vocabulary(string_b)
        return frozenset(map(lambda x: sort_fluents(string_from_components(x)), superpose(string_a, string_b, vocab_a, vocab_b)))

    if not components_a and not components_b:
        return [[]]
    if not components_a or not components_b:
        return []

    # first one was old version, not sure if new one is technically correct or not, but gives better results
    if frozenset(vocab_a) & frozenset(components_b[0]) <= frozenset(components_a[0]) and frozenset(vocab_b) & frozenset(components_a[0]) <= frozenset(components_b[0]):
    # if frozenset(vocab_a) & frozenset([x for x in components_b[0] if not x.startswith('!')]) <= frozenset([x for x in components_a[0] if not x.startswith('!')]) and frozenset(vocab_b) & frozenset([x for x in components_a[0] if not x.startswith('!')]) <= frozenset([x for x in components_b[0] if not x.startswith('!')]):
        head_union = nonempty_union(components_a[0], components_b[0])
        
        # removes '|a|b| & |!a|b|' cases
        if remove_negated_pairs:
            for zz in head_union:
                if zz.startswith('!') and zz[1:] in head_union:
                    return []
        
        l = L(components_a[0], components_a[1:], vocab_a, components_b[0], components_b[1:], vocab_b)
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

from functools import lru_cache

@lru_cache(maxsize=100)
def superpose_sensible(a, b, limit = 0):
    if a == b:
        return [frozenset([a])]
    v_a = vocabulary(a)
    v_b = vocabulary(b)
    if v_a == v_b:
        return []
        # raise Exception('Strings containing '+a+' and '+b+' could not be superposed as they are inconsistent.')
    elif len(v_a & v_b) == 0:
        return [frozenset([a]), frozenset([b])]
    else:
        sp = superpose(a, b)
        # if string_length(a) > 0 and string_length(b) > 0 and len(sp) == 0:
        #     raise Exception('Strings containing '+block_compress(reduct(a, v_a & v_b))+' and '+block_compress(reduct(b, v_a & v_b))+' could not be superposed as they are inconsistent.')
        if limit > 0 and len(sp) > limit:
            return [frozenset([a]), frozenset([b])]
        else:
            return [sp]

def superpose_langs_sensible(lang1, lang2, limit = 0):
    yield from set([item for s1 in lang1 for s2 in lang2 for sublist in superpose_sensible(s1, s2, limit) for item in sublist])
    
# def superpose_langs_sensible(lang1, lang2, limit = 0):
#     results = []
#     for s1 in lang1:
#         for s2 in lang2:
#             results += [item for sublist in superpose_sensible(s1, s2, limit) for item in sublist]
#     yield from set(results)

# def superpose_all_langs_sensible(list_of_langs, limit = 0):
#     if type(list_of_langs) != list:
#         raise TypeError
#     elif len(list_of_langs) == 0:
#         raise Exception('Cannot use empty list')
#     elif len(list_of_langs) == 1:
#         results = dict()
#         for s in list_of_langs[0]:
#             v = vocabulary(s)
#             if v in results and s not in results[v]:
#                 results[v].append(s)
#             else:
#                 results[v] = [s]
#         yield from results.values()
#     else:
#         sp = list(superpose_langs_sensible(list_of_langs[0], list_of_langs[1], limit))
#         yield from superpose_all_langs_sensible([sp]+list_of_langs[2:], limit)

def superpose_all_langs_sensible(list_of_langs, limit = 0):
    yielded = False
    for i, l in enumerate(list_of_langs):
        for j, ll in enumerate(list_of_langs[i+1:]):
            if yielded:
                break
            sp = list(superpose_langs_sensible(l, ll, limit))
            if sp == []:
                raise Exception('Contradiction: {} and {}'.format(l, ll))
            elif set(l + ll) == set(sp):
                pass # no sp
            else:
                yielded = True
                yield from superpose_all_langs_sensible([sp]+list_of_langs[i+1:i+1+j]+list_of_langs[i+1+j+1:], limit)
    if not yielded:
        yield from list_of_langs

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
    except IndexError as e:
        # print(e)
        return []
        # for l in list_of_langs:
        #     print([hide_negated(s) for s in l])
        # print('---')
        # print(checks)

def flatten_list(deep_list):
    return [item for sublist in deep_list for item in sublist]

def gap(premises, conclusion):
    sl = superpose_langs(premises, conclusion)
    presiduals = frozenset()
    for s in sl:
        for proj in [projection(s, v) for v in subsets(vocabulary(s))]:
            prem_proj = flatten_list([superpose(proj, prem) for prem in premises])
            if all(string_equals(projection(pp, vocabulary(c)), c) for c in conclusion for pp in prem_proj):
                presiduals.add(proj)
    minimal = []
    for r in presiduals:
        if all(projection(r, v) not in presiduals for v in proper_subsets(vocabulary(r))):
            minimal.append(r)
    return minimal

def pw_sp(string_a, string_b, vocab_a = None, vocab_b = None):
    zipl = itertools.zip_longest
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