import os
import re
import collections

from string_functions import superpose, superpose_all_langs, superpose_all_langs_pick_shortest, block_compress, reduct, vocabulary

CORPUS_PATH = '/home/david/pgrad/PMB-analysis/pmb-3.0.0/data/en/gold/'

def corpus_crawler(corpus_dir, filename = 'en.drs.clf'):
    result = []
    parts = os.listdir(corpus_dir)
    for part in parts:
        docs = os.listdir(corpus_dir + part)
        for doc in docs:
            result.append(part + '/' + doc + '/' + filename)
    return result

def predicate_frequencies(clauses, temporal_only = True, no_lowercase = False):
    if temporal_only:
        clauses = map(filter_clauses, clauses)
    all_doc_clauses = [clause for doc in clauses for clause in doc]
    predicates = list(map(lambda x: x.split()[1] if len(x) > 0 else '', all_doc_clauses))
    if no_lowercase:
        predicates = [predicate for predicate in predicates if not predicate.islower()]
    return collections.Counter(predicates)

def parse_clf(clf_file):
    clauses = []
    with open(clf_file, 'r') as f:
        for line in f:
            if not line.startswith('%'):
                clauses.append(line.split('%')[0].rstrip())
    return clauses

# def filter_clauses(clauses):
#     result = []
#     for clause in clauses:
#         if (re.search(r' [et][0-9]+', clause) or re.search(r'b[0-9]+ [A-Z]+ b[0-9]+', clause)) and not re.search(r' [xs][0-9]+', clause): # remove s to allow for statives
#             result.append(clause)
#     return result

def split_clauses(clauses):
    temporal = []
    discourse = []
    rest = []
    for clause in clauses:
        if re.search(r' [et][0-9]+', clause) and not re.search(r' [xs][0-9]+', clause): # remove s to allow for statives
            temporal.append(clause)
        elif re.search(r'b[0-9]+ [A-Z]+ b[0-9]+', clause):
            discourse.append(clause)
        else:
            rest.append(clause)
    return (temporal, discourse, rest)

def parse_discourse_clause(clause):
    elements = clause.split()
    boxA = elements[0]
    relation = elements[1]
    boxB = elements[2]
    if relation in ['CONDITION', 'CONSEQUENCE']:
        raise Exception('Can\'t handle discourse relations of type [' + relation + '] yet.')
    # elif relation in ['CONTINUATION']:
    #     return ['|' + boxA + '||' + boxB + '|']
    elif relation in ['ATTRIBUTION', 'PRESUPPOSITION', 'NEGATION', 'CONTINUATION']:
        return ['|' + boxA + ',' + boxB + '|']
    # elif relation in ['EXPLANATION']:
    #     return []
    else:
        return []

def parse_temporal_clause(clause):
    elements = clause.split()
    box = elements[0]
    predicate = elements[1]
    rest = elements[2:]
    if predicate in ['REF']:
        return ['|' + box + '|' + box + ',' + rest[0] + '|' + box + '|']
    elif predicate in ['Time', 'EQU']:
        return ['|' + ','.join(rest) + '|']
    elif predicate.islower() and rest[0].startswith('"v.'):
        return ['|' + predicate + ',' + rest[1] + '|']
    elif predicate in ['TPR']:
        return ['|' + '||'.join(rest) + '|']
    elif predicate in ['TAB']:
        return ['|' + '|'.join(rest) + '|']

    else:
        return []

def langs_from_clf(clf):
    clauses = parse_clf(clf)
    (temporal, discourse, _rest) = split_clauses(clauses)
    disc = list(map(parse_discourse_clause, discourse))
    temp = list(map(parse_temporal_clause, temporal))
    return [lang for lang in temp+disc if len(lang) > 0]

def hide_identifiers(string):
    v = vocabulary(string)
    nv = [i for i in v if not re.match(r'[bet][0-9]+', i)]
    return block_compress(reduct(string, nv))



#TODO: discourse relations
# ATTRIBUTION - events with others as arguments
# EXPLANATION - older relation - should make parse_clause_to_lang return langs not strings

corpus = corpus_crawler(CORPUS_PATH)

# clauses =  map(parse_clf, map(lambda x: CORPUS_PATH+x, corpus))
# cc = predicate_frequencies(clauses, True, True)
# print(len(cc))
# print(cc)

# langs = map(langs_from_clf, map(lambda x: CORPUS_PATH+x, corpus[:100]))
langs = []
for f in corpus:
    try:
        langs.append(langs_from_clf(CORPUS_PATH + f))
    except:
        langs.append([])

count = 0
# fcount = 0
for lang in langs[:1000]:#[:1000]:
    if len(lang) > 0:
        print(corpus[count])
        # print(lang)
        try:
            sps = list(superpose_all_langs_pick_shortest(lang))
            # print(list(frozenset(map(lambda x: x, sps))), '=>', corpus[count])
            res = list(frozenset(map(hide_identifiers, sps)))
            if len(res) > 0:
                print(res)
                pass
            else:
                # print([], '=>', corpus[count])
                # fcount += 1
                pass
        except Exception as e:
            print(e)
            print(lang)
            print(corpus[count])
            break
    else:
        print([], '=>', corpus[count])
        # fcount += 1
    # print(lang, '=>', corpus[count])
    count += 1
    print()

# print('failure count:', fcount, 'of', count)