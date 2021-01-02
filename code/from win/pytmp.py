from string_functions import *
import re

cache = dict()
def get_cached_L_A(symset):
    global cache
    k = ','.join(sorted(symset))
    if k not in cache:
        s = set(depad(sp) for s in subsets(symset) if len(s) > 0 for sp in hacked_point_sp_all(list(s)))
        s.add('')
        cache[k] = s
    return cache.get(k)

# hacky, checks for symbols occuring in more than one box
def contains_interval(string):
    listOfElems = flatten_list(x.split(',') for x in string.replace(' ', '').split('|') if x != '')
    setOfElems = set()
    for elem in listOfElems:
        if elem in setOfElems:
            return True
        else:
            setOfElems.add(elem)         
    return False

def depad(string):
    return '|'.join(c for c in string.replace(' ', '').split('|') if c != '')

def d_projection(string, proj_set):
    return depad(reduct(string, proj_set))

def sem_eval(string, symset):
    L_A = get_cached_L_A(symset)
    v = vocabulary(string)
    return set([s for s in L_A if string_equals(d_projection(s, v), string)])

def sem_eval_lang(lang, symset):
    ret = set()
    for string in lang:
        ret |= sem_eval(string, symset)
    return ret

def hacked_point_sp(s1, s2):
    return set(map(lambda x: depad(x), filter(lambda x: not contains_interval(x), superpose('|'+s1+'|', '|'+s2+'|'))))

def hacked_point_sp_all(strs):
    if type(strs) != list:
        raise TypeError
    elif len(strs) == 0:
        raise Exception('Cannot use empty list')
    elif len(strs) == 1:
        return [strs[0]]
    else:
        res = []
        for sp in set(filter(lambda x: not contains_interval(x), superpose('|'+strs[0]+'|', '|'+strs[1]+'|'))):
            res.append(hacked_point_sp_all([sp] + strs[2:]))
        return set(map(lambda x: depad(x), flatten_list(res)))

def pw_gap(i_premises, i_conclusion):
    sl = hacked_point_sp_all(i_premises + i_conclusion)
    premises = list(map(lambda x: depad(x), i_premises))
    conclusion = list(map(lambda x: depad(x), i_conclusion))
    presiduals = set()
    for s in sl:
        for proj in [d_projection(s, v) for v in subsets(vocabulary(s))]:
            prem_proj = flatten_list([hacked_point_sp(proj, prem) for prem in premises])
            if all(string_equals(d_projection(pp, vocabulary(c)), c) for c in conclusion for pp in prem_proj):
                presiduals.add(proj)
    minimal = set()
    for r in presiduals:
        if all(d_projection(r, v) not in presiduals for v in proper_subsets(vocabulary(r))):
            minimal.add(r)
    return minimal

def res(conclusion, premises, symset):
    L_A = get_cached_L_A(symset)
    prem_eval = sem_eval_lang(premises, symset)
    # print(prem_eval)
    conc_eval = sem_eval_lang(conclusion, symset)
    # print(conc_eval)
    # return set(s for s in L_A if sem_eval(s, symset) & prem_eval <= conc_eval)
    ret = set()
    for s in L_A:
        s_eval = sem_eval(s, symset)
        inter = s_eval & prem_eval
        # print(s, s_eval, inter)
        if inter <= conc_eval:# and len(inter) > 0: #?
            # print('added')
            ret.add(s)
        # print()
    return ret

def lang_subsumption(L1, L2):
    return all(string_equals(d_projection(s1, vocabulary(s2)), s2) for s2 in L2 for s1 in L1)

def down_set(L):
    ret = set()
    for s in L:
        for v in subsets(vocabulary(s)):
            ret.add(d_projection(s, v))
    return ret
########
# l1 = ['|year(1992)|year(1992), location(x,y)|location(x,y)|', '|year(1996), now|']
# l2 = ['|year(1993), location(x,y)|']
# l1 = ['|a|a,b|b|', '|c,d|']
# l2 = ['|e,b|']
A = ['a', 'b', 'c']
l1 = ['|b||c|']
l2 = ['|a||c|']

# print(gap(l1, l2))

# print(pw_gap(l1, l2))

# print(hacked_point_sp('a', 'b'))
# print(list(hacked_point_sp_all(['a', 'b', 'c'])))

# print(sem_eval('a,b', ['a','b','c']))
# print(sem_eval('a|b', ['a','b','c']))
# print(sem_eval('a|c', ['a','b','c']))
# print(sem_eval_lang(['a,b', 'a|b','a|c'], ['a','b','c']))
# r = res(['a|c'], ['b|c'], A)

# r = res([], ['b|c'], A)
# print()
# print(r)
# print(pw_gap([], l2))


# print(lang_subsumption(['a|b|c', 'b|c|d'], ['b|c']))
# print(down_set(['a|b,c']))


# print(get_cached_L_A(A))
# print()

L_and_L = hacked_point_sp_all(['a||c', 'b||c'])
# print(L_and_L)
# print(down_set(L_and_L))
# sdll = sem_eval_lang(down_set(L_and_L), A)
# print(sdll)
# print('diff LA - sdll', get_cached_L_A(A) - sdll)
# print('diff sdll - LA',  sdll - get_cached_L_A(A))


# print(sem_eval_lang(['a|c'], A) & sem_eval_lang(['b|c'], A))

# pll = set()
# for s in down_set(L_and_L):
#     if lang_subsumption(hacked_point_sp_all([s]+['b|c']), ['a|c']):
#         pll.add(s)
# print(pll)
# mpll = set()
# for r in pll:
#     if all(d_projection(r, v) not in pll for v in proper_subsets(vocabulary(r))):
#         mpll.add(r)
# print(mpll)

# print(sem_eval_lang(pll, A) == sem_eval_lang(mpll, A))

inter = res(['a|c'], ['b|c'], A) & down_set(L_and_L)
# print(inter)
rg = sem_eval_lang(inter, A)
sg = sem_eval_lang(pw_gap(l1, l2), A)
# print(rg)
# print(sg)
# print(rg == sg)

# print('res = rg',res(['a|c'], ['b|c'], A) == rg)