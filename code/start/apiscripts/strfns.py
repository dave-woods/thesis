from functools import reduce, lru_cache
from collections import Counter
import itertools
import re

def negate_component(component, as_string=False):
    """Take a component, and return it with all its fluents negated"""
    c = list(map(lambda f: f[1:] if f == '' or f.startswith('!') else '!'+f, component))
    return c if not as_string else ','.join(c)

def negate_string(string):
    """Take a string, and return it with every component negated"""
    return '|'.join([','.join(c) for c in map(negate_component, get_components(string))])

def hide_negated(string):
    """Take a string and filter out any negated fluents"""
    newc = []
    for c in get_components(string):
        newc.append(list(filter(lambda f: not f.startswith('!'), c)))
    return '|'.join([','.join(c) for c in newc])

def subsets(s):
    """Take an iterable and return the set of its subsets"""
    return frozenset(frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1)))

def proper_subsets(s):
    """Take an iterable and return the set of its proper subsets"""
    return frozenset(frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s))))

def nonempty_union(x, y):
    """Take two sets and return their union"""
    try:
        z = frozenset(x) | frozenset(y)
    except:
        z = x + y
    return list(filter(None, z)) if len(z) > 1 else list(z)

def get_components(string):
    """Take a string and return a list of components"""
    try:
        return [s.split(',') for s in string.replace(' ', '').split('|')]
    except AttributeError:
        return string

def string_from_components(components):
    """Take a list of components and return a string"""
    return '|'.join([','.join(c) for c in components])

def vocabulary(string):
    """Take a string, return its vocabulary as a set"""
    if string == '' or string == []:
        return frozenset()
    try:
        components = get_components(string)
        return frozenset(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), components)))
    except AttributeError:
        return frozenset(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), string)))

def vocabulary_lang(lang):
    """Take a language, return its vocabulary"""
    return frozenset(reduce(lambda x, y: list(vocabulary(x) | vocabulary(y)), lang, []))

def string_length(string):
    """Take a string, return the number of components it has"""
    return len(string.split('|'))

def sort_fluents(string):
    """Take a string, return a string with all its fluents alphabetised within their components"""
    return '|'.join([','.join(sorted(x.split(','))) for x in string.split('|')])

def string_equals(a, b):
    """Take two strings, return whether they contain the same data"""
    return [sorted(x.split(',')) for x in a.split('|')] == [sorted(x.split(',')) for x in b.split('|')]

def reduct(string, new_vocab):
    """Take a string and a set, return the string with its vocab set to the set"""
    components = get_components(string)
    reducted = [[f for f in c if f in new_vocab] for c in components]
    return '|'.join([','.join(c) for c in reducted])

def block_compress(string):
    """Take a string, return the string without stutter"""
    components = get_components(string)
    if len(components) < 2:
        return '|'.join([','.join(c) for c in components])
    elif Counter(components[0]) == Counter(components[1]):
        return block_compress('|'.join([','.join(c) for c in components[1:]]))
    else:
        return ','.join(components[0]) + '|' + block_compress('|'.join([','.join(c) for c in components[1:]]))

def projection(string, proj_set):
    """Take a string and a set, return the block compressed reduct"""
    return block_compress(reduct(string, proj_set))

def projection_lang(lang, new_vocab):
    """Take a language and a set, return the block compressed reduct of every string in the language"""
    return list(set(filter(lambda n: n != '', [projection(s, new_vocab) for s in lang])))

def string_projects_to_string(a, b):
    """Take two strings, return whether the first projects to the second"""
    return string_equals(b, projection(a, vocabulary(b)))

def lang_projects_to_string(a, b):
    """Take a language and a string, return whether the first projects to the second"""
    return all([string_projects_to_string(s, b) for s in a])

def lang_projects_to_lang(a, b):
    """Take two languages, return whether the first projects to the second"""
    return all([lang_projects_to_string(a, s) for s in b])

def lang_contains_string(a, b):
    """Take a language and a string, return whether the first contains the second"""
    return any([string_projects_to_string(s, b) for s in a])

def lang_contradicts_string(a, b):
    """Take a language and a string, return whether the first contradicts the second"""
    return not lang_contains_string(a,b) and any([vocabulary(s).issuperseteq(vocabulary(b)) for s in a])

def projection_full_vocab(string, vocab):
    """Take a string and a set, return the block compressed reduct or an empty string if the full vocab isn't used"""
    p = projection(string, vocab)
    return p if vocabulary(p) == frozenset(vocab) else ''

def projection_lang_full_vocab(lang, new_vocab):
    """Take a language and a set, return the block compressed reduct of every string in the language or empty strings if the full vocab isn't used"""
    return list(set(filter(lambda n: n != '', [projection_full_vocab(s, new_vocab) for s in lang])))

def analogous_strings(a, b):
    """Take two strings and return whether they are analogous"""
    v_a = vocabulary(a)
    v_b = vocabulary(b)
    mapping = dict()
    for v in v_a:
        for w in v_b.difference(frozenset(mapping.values())):
            if reduct(a, [v]) == reduct(b, [w]).replace(w, v):
                mapping[v] = w
                break
    return frozenset(mapping.keys()) == v_a and frozenset(mapping.values()) == v_b, mapping

def basic_sp(string_a, string_b):
    """Take two strings, return their basic superposition (a string)"""
    components_a = get_components(string_a)
    components_b = get_components(string_b)
    return sort_fluents(string_from_components([nonempty_union(a, b) for (a, b) in zip(components_a, components_b)]))

def basic_sp_lang(lang_a, lang_b):
    """Take two languages, return their basic superposition (a language)"""
    result = []
    for a in lang_a:
        for b in lang_b:
            result.append(basic_sp(a, b))
    return frozenset(result)

def pad(string, length):
    """Take a string and an int, and pad the string to the length of the int"""
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

def async_sp(string_a, string_b):
    """Take two strings and return their asynchronous superposition (a language)"""
    len_a = string_length(string_a)
    len_b = string_length(string_b)
    pad_len = len_a + len_b - 1
    padded_a = pad(string_a, pad_len)
    padded_b = pad(string_b, pad_len)
    return frozenset(map(lambda s: block_compress(s), basic_sp_lang(padded_a, padded_b)))

def superpose(string_a, string_b, vocab_a = None, vocab_b = None, remove_negated_pairs = True):
    """Take two strings and return their vocabulary-constrained superposition (a language)"""
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

    if frozenset(vocab_a) & frozenset(components_b[0]) <= frozenset(components_a[0]) and frozenset(vocab_b) & frozenset(components_a[0]) <= frozenset(components_b[0]):
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
    """Part of vocabulary-constrained superposition"""
    part_1 = superpose([head_a] + tail_a, tail_b, vocab_a, vocab_b)
    part_2 = superpose(tail_a, [head_b] + tail_b, vocab_a, vocab_b)
    part_3 = superpose(tail_a, tail_b, vocab_a, vocab_b)
    return nonempty_union(nonempty_union(part_1, part_2), part_3)

def superpose_all(list_of_strings):
    """Take a list of strings, return the result of superposing them all (a language)"""
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
    """Take a pair of languages, return their superposition (a language)"""
    for s1 in lang1:
        for s2 in lang2:
            yield from superpose(s1, s2)

def superpose_all_langs(list_of_langs, filt=None):
    """Take a list of languages with an optional filter for external constraints, return the result of superposing them all (a language)"""
    running = list_of_langs[0]
    for lang in list_of_langs[1:]:
        yield running
        running = [s for s in superpose_langs(running, lang) if filt is None or filt(s)]
    yield running

@lru_cache(maxsize=1000)
def superpose_sensible(a, b, limit = 0):
    """Take two strings and a limit, return the superposition of the strings (a language) where it sensible to do so"""
    if sort_fluents(a) == sort_fluents(b):
        return [frozenset([a])]
    v_a = vocabulary(a)
    v_b = vocabulary(b)
    if v_a == v_b:
        return []
    elif len(v_a & v_b) == 0:
        return [frozenset([a]), frozenset([b])]
    else:
        sp = superpose(a, b)
        if limit > 0 and len(sp) > limit:
            return [frozenset([a]), frozenset([b])]
        else:
            return [sp]

def superpose_langs_sensible(lang1, lang2, limit = 0):
    """Take two languages and a limit, return the superposition of the languages (a language) where it sensible to do so"""
    yield from set([item for s1 in lang1 for s2 in lang2 for sublist in superpose_sensible(s1, s2, limit) for item in sublist])

def superpose_all_langs_sensible(list_of_langs, limit = 0):
    """Take a list of languages and a limit, return the superposition of the languages (a list of languages)"""
    yielded = False
    for i, l in enumerate(list_of_langs):
        for j, ll in enumerate(list_of_langs[i+1:]):
            if yielded:
                break
            sp = list(superpose_langs_sensible(l, ll, limit))
            if sp == []:
                raise Exception('Contradiction: {} and {}'.format(l, ll))
            elif set(l + ll) == set(sp) or (limit > 0 and len(sp) > limit):
                pass # no sp
            else:
                yielded = True
                yield from superpose_all_langs_sensible([sp]+list_of_langs[:i]+list_of_langs[i+1:i+1+j]+list_of_langs[i+1+j+1:], limit)
    if not yielded:
        yield from list_of_langs

def flatten_list(deep_list):
    """Take a nested list and return it flattened"""
    return [item for sublist in deep_list for item in sublist]

def gap(premises, conclusion):
    """Take two languages and return the set of strings which, when superposed with the premises, would entail the conclusion"""
    sl = superpose_langs(premises, conclusion)
    presiduals = set()
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

def most_simultaneous_events_occurring(string):
    """Take a string and return the size of the largest component"""
    return max(map(lambda c: len(c), get_components(string)))

def least_simultaneous_resources(strings):
    """Take a list of strings and return the list sorted by whish uses the least simultaneous resources"""
    min_set = set([strings[0]])
    min_len = most_simultaneous_events_occurring(strings[0])
    for s in strings[1:]:
        l = most_simultaneous_events_occurring(s)
        if l < min_len:
            min_len = l
            min_set = set([s])
        elif l == min_len:
            min_set.add(s)
    return sorted(min_set, key=lambda s: string_length(s))

def to_semiintervals(string, keep_fluents=False):
    """Take a string containing interval fluents, return its translation to use semi-intervals"""
    vocab = vocabulary(string)
    pp = map(lambda v: ('α({})'.format(v),'ω({})'.format(v)), vocab)
    lookup = { v: p for v, p in zip(vocab, pp) }
    used = []
    result = []
    for c in get_components(string):
        used += [f for f in c if f != '']
        # pre if fluent not occurred + post if occurred
        new_c = [lookup[k][0] for k in lookup if k not in used and k not in c] + [lookup[k][1] for k in lookup if k in used and k not in c]
        result.append(new_c if not keep_fluents else new_c + [f for f in c if f != ''])
    return '|'.join([','.join(c) for c in result])

def from_semiintervals(string):
    """Take a string containing semi-interval fluents, return its translation to use intervals"""
    vocab = set(re.findall(r'[αω]\((\w+)\)', string))
    pp = map(lambda v: ('α({})'.format(v),'ω({})'.format(v)), vocab)
    lookup = { v: p for v, p in zip(vocab, pp) }
    used = []
    result = []
    for c in get_components(string):
        used += [k for k in lookup if lookup[k][1] in c]
        result.append([k for k in lookup if k not in used and lookup[k][0] not in c])
    return '|'.join([','.join(c) for c in result])