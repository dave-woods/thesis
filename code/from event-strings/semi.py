from functools import reduce
import re
import freksa
from string_functions import block_compress, reduct, get_components, vocabulary, superpose, nonempty_union

# Only places one pre/post per string
def translate_only_one(string):
    components = [s.split(',') for s in string.replace(' ', '').split('|')]
    used = []
    result = []
    for i, c in enumerate(components):
        new_c = []
        if i < len(components) - 1:
            for f in components[i+1]:
                if f == '':
                    continue
                pre = 'α({})'.format(f)
                if pre not in used:
                    new_c.append(pre)
                    used.append(pre)
        if i > 0:
            for f in components[i-1]:
                if f == '':
                    continue
                post = 'ω({})'.format(f)
                if post not in used:
                    new_c.append(post)
                    used.append(post)
        result.append(new_c)
    return ('|'.join([','.join(c) for c in result]), string)

def translate(string, keep_fluents=False):
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

def reverse_translate(string):
    # lookup = dict(set(re.findall(r'([αω]\((\w+)\))', string)))
    vocab = set(re.findall(r'[αω]\((\w+)\)', string))
    pp = map(lambda v: ('α({})'.format(v),'ω({})'.format(v)), vocab)
    lookup = { v: p for v, p in zip(vocab, pp) }
    used = []
    result = []
    for c in get_components(string):
        used += [k for k in lookup if lookup[k][1] in c]
        result.append([k for k in lookup if k not in used and lookup[k][0] not in c])
    return '|'.join([','.join(c) for c in result])
                


def to_borders(string):
    s1 = [s.split(',') for s in string.replace(' ', '').split('|')]
    ns = []
    for i, b in enumerate(s1):
        nb = []
        if i == len(s1) - 1:
            pass
        else:
            for f in s1[i+1]:
                if f != '' and f not in b:
                    nb.append('l({})'.format(f))
            for f in b:
                if f != '' and f not in s1[i+1]:
                    nb.append('r({})'.format(f))
        ns.append(nb if len(nb) > 0 else [''])
    return '|'.join([','.join(c) for c in ns])

def enhanced_reduct(string, new_vocab):
    components = get_components(string)
    reducted = []
    for c in components:
        reducted.append(set([d for f in c for d in new_vocab if f in d.split('/')] + [d for d in new_vocab if all(dd in c for dd in d.split('^'))]))
    return '|'.join([','.join(c) for c in reducted])

def bcrd(string, alpha):
    return block_compress(enhanced_reduct(string, alpha))


# l = list(map(translate, freksa.un('a', 'b')))
# for ll in l:
    # print((ll[1], ll[0], bcrd(ll[0], ['α(a)','α(b)']), bcrd(ll[0], ['α(a)','ω(b)']), bcrd(ll[0], ['ω(a)','α(b)']), bcrd(ll[0], ['ω(a)','ω(b)'])))

# for s in freksa.ct('a', 'b'):
#     # print(s, translate(s), reverse_translate(translate(s)))
#     print(bcrd(translate(s), ['α(a)', 'α(b)', 'ω(a)', 'ω(b)']))



    
def string_length(string):
    return len(string.split('|'))

def string_equals(a, b):
    return [sorted(x.split(',')) for x in a.split('|')] == [sorted(x.split(',')) for x in b.split('|')]

def projection(string, proj_set):
    return bcrd(string, proj_set)

def projects_to(a, b):
    return string_equals(b, projection(a, vocabulary(b)))

def to_latex(string):
    return '\EventString{' + re.sub(r'\|$', '|{}', re.sub(r'^\|', '{}|', string)).replace('||', '|{}|').replace('/', '\lor').replace('α', '\\alpha').replace('ω', '\omega') + '}'
    # return '\ebox{' + string.replace('|', '}\ebox{').replace('/', '\lor').replace('α', '\\alpha').replace('ω', '\omega') + '}'

def checker():
    frek = [('un', 'α(a)/α(b)/ω(a)/ω(b)/'), ('ol', 'α(a),α(b)|α(b)|'), ('yo', 'α(a),α(b)|α(a)|'), ('hh', 'α(a),α(b)|'), ('tt', '|ω(a),ω(b)'), ('sv', '|ω(b)|ω(a),ω(b)'), ('sb', '|ω(a)|ω(a),ω(b)'), ('bd', 'α(a)||ω(b)'), ('db', 'α(b)||ω(a)'), ('pr', 'α(b)/ω(a)'), ('sd', 'α(a)/ω(b)'), ('ct', 'α(a)/α(b)||ω(a)/ω(b)'), ('oc', 'α(a),α(b)|α(b)||ω(a)/ω(b)'), ('yc', 'α(a),α(b)|α(a)||ω(a)/ω(b)'), ('sc', 'α(a)||ω(b)|ω(a),ω(b)'), ('bc', 'α(b)||ω(a)|ω(a),ω(b)')] # not worked out: ob, ys, un
    unknown = list(map(translate, freksa.un('a', 'b')))

    for rel, string in frek:
        r = list(map(translate, getattr(freksa, rel)('a', 'b')))
        condition1 = all(projects_to(s, string) for s in r)
        condition2 = len([x for x in map(lambda s: projects_to(s, string), unknown) if x]) == len(list(r))
        try:
            assert(condition1)
            assert(condition2)
        except AssertionError:
            print('Assertion failed:')
            print(rel, string)
            print(r)

#######

# checker()
# print('α(a),α(b)|α(b)||ω(b)/ω(a)', to_latex('α(a),α(b)|α(b)||ω(b)/ω(a)'))

#######

# for s in freksa.ob('a', 'b'):
#     ts = translate(s, True)
#     print(s, ts)

# print()
# idx = 1
# for s in getattr(freksa, 'un')('a', 'b'):
#     ts = translate(s, True)
#     cj = enhanced_reduct(ts, ['a^α(b)', 'ω(a)/', 'ω(a)^ω(b)'])
#     print(idx, block_compress(cj))
#     idx += 1

#######

# print(translate(freksa.b('a', 'b')[0]))
# print(translate(freksa.pr('a', 'b')[1]))
# 'α(b)/ω(a)'

# before = translate(freksa.b('a', 'b')[0])
# precedes = 'α(b)/ω(a)'
# succeeds = 'α(a)/ω(b)'

# print('old, should be empty ', superpose('|x||y|', 'x'))
# print('old, should be before', superpose(before, precedes))
# print('old, should be empty ', superpose(before, succeeds))

# print()

def modified_vocab(components):
    return set(filter(None, reduce(lambda x, y: list(set(x) | set([yyy for yy in y for yyy in yy.split('/')])), components, set())))

def modified_superpose(string_a, string_b, vocab_a = None, vocab_b = None):
    if vocab_a is None and vocab_b is None:
        components_a = get_components(string_a)
        components_b = get_components(string_b)
        vocab_a = modified_vocab(components_a)
        vocab_b = modified_vocab(components_b)
        splist = ['|'.join([','.join(s) for s in string_r]) for string_r in modified_superpose(components_a, components_b, vocab_a, vocab_b)]
        return splist

    if not string_a and not string_b:
        return [[]]
    if not string_a or not string_b:
        return []

    # if set(vocab_a) & set(string_b[0]) <= set(string_a[0]) and set(vocab_b) & set(string_a[0]) <= set(string_b[0]):
    if any(vocab_a & y <= modified_vocab([string_a[0]]) for y in component_to_disjunct_sets(string_b[0])) and any(vocab_b & x <= modified_vocab([string_b[0]]) for x in component_to_disjunct_sets(string_a[0])):
    # if set(vocab_a) & set([x for x in string_b[0] if not x.startswith('!')]) <= set([x for x in string_a[0] if not x.startswith('!')]) and set(vocab_b) & set([x for x in string_a[0] if not x.startswith('!')]) <= set([x for x in string_b[0] if not x.startswith('!')]):
        head_union = nonempty_union(string_a[0], string_b[0])
        
        # removes '|a|b| & |!a|b|' cases
        for zz in head_union:
            if zz.startswith('!') and zz[1:] in head_union:
                return []
        
        l = modified_L(string_a[0], string_a[1:], vocab_a, string_b[0], string_b[1:], vocab_b)
        return [[head_union] + l_item for l_item in l]

    return []

# [a, b] -> [{a,b}]
# [a, b/c] -> [{a,b}, {a,c}]
# [a/b, c] -> [{a,c}, {b,c}]
# [a/b, c/d] -> [{a,c}, {a,d}, {b,c}, {b,d}]
# [a/b/c, d] -> [{a,d}, {b,d}, {c,d}]
def component_to_disjunct_sets(component, found = set()):
    if len(component) < 1: return [found]
    result = [component_to_disjunct_sets(component[1:], set([c]) | found) for c in component[0].split('/')]
    return [i for s in result for i in s]

def remove_disjunct_fluents(string):
    nc = [[f for f in c if '/' not in f] for c in [s.split(',') for s in string.replace(' ', '').split('|')]]
    return '|'.join([','.join(c) for c in nc])

def modified_L(head_a, tail_a, vocab_a, head_b, tail_b, vocab_b):
    part_1 = modified_superpose([head_a] + tail_a, tail_b, vocab_a, vocab_b)
    part_2 = modified_superpose(tail_a, [head_b] + tail_b, vocab_a, vocab_b)
    part_3 = modified_superpose(tail_a, tail_b, vocab_a, vocab_b)
    return nonempty_union(nonempty_union(part_1, part_2), part_3)

# print('new, should be empty ', modified_superpose('|x||y|', 'x'))
# print('new, should be before', modified_superpose(before, precedes))
# print('new, should be empty ', modified_superpose(before, succeeds))
# print('new,                 ', modified_superpose(precedes, succeeds))
# print('new,                 ', modified_superpose('|x||y|', '|z|y,z|y|'))
# # ('sc', 'α(a)||ω(b)|ω(a),ω(b)'), ('bc', 'α(b)||ω(a)|ω(a),ω(b)') ('ct', 'α(a)/α(b)||ω(a)/ω(b)'), ('oc', 'α(a),α(b)|α(b)||ω(a)/ω(b)')
# print('new,                 ', modified_superpose('α(a)||ω(b)|ω(a),ω(b)', translate(freksa.oi('a', 'b')[0])))
# print('new,                 ', list(map(lambda x:x, modified_superpose('α(a)||ω(b)|ω(a),ω(b)', 'α(a)/α(b)||ω(a)/ω(b)'))))
# print('new,                 ', list(map(lambda x:x, modified_superpose('α(a),α(b)|α(b)||ω(a)/ω(b)', 'α(a)/α(b)||ω(a)/ω(b)'))))
# #TODO: should remove disjunctions iff they are satisfied in the same component i.e. |a/b,a| -> |a|, but |a/b| -> |a/b|
# #      should this be done during superposition?

# durand + schwer train problem 2008
results = []
ms = modified_superpose('α(A),α(B),α(E)|', '|ω(A)|ω(A),ω(B)')
for s in ms:
    mm = modified_superpose(s, 'α(D),α(F)||ω(B)')
    for m in mm:
        mmm = modified_superpose(m, '|ω(E),ω(D)')
        for m1 in mmm:
            mm1 = modified_superpose(m1, 'α(D)|ω(C),α(D)|ω(A),ω(C)')
            for x1 in mm1:
                if set(vocabulary(reverse_translate(x1))) == set(['A', 'B', 'C', 'D', 'E', 'F']): 
                    results.append(reverse_translate(x1))
            mm2 = modified_superpose(m1, 'α(D)|ω(A),ω(C)')
            for x1 in mm2:
                if set(vocabulary(reverse_translate(x1))) == set(['A', 'B', 'C', 'D', 'E', 'F']): 
                    results.append(reverse_translate(x1))


# this is incorrect
def optimal_resources(strings):
    min_len = string_length(strings[0])
    min_set = set([strings[0]])
    for s in strings[1:]:
        l = string_length(s)
        if l < min_len:
            min_len = l
            min_set = set([s])
        elif l == min_len:
            min_set.add(s)
    min_sorted = sorted(min_set, key=lambda s: reduce(lambda acc, cur: acc + len(cur), s.split('|'), 0))
    return {'least_resources': min_sorted[0], 'least_time': min_sorted[-1]}

for k, v in optimal_resources(results).items():
    print(k, v, string_length(v))
