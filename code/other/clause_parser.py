import os
import re
import collections
import argparse

import freksa
from net_analyser import sense_to_semantics, sem_to_string
from string_functions import superpose, superpose_all_langs, superpose_all_langs_pick_shortest, block_compress, reduct, vocabulary

def parse_clf(clf_file):
    clauses = []
    text = ''
    lidx = 0
    with open(clf_file, 'r') as f:
        for line in f:
            if not line.startswith('%'):
                clauses.append(line.split('%')[0].rstrip())
            elif lidx == 2:
                text = line[4:].rstrip()
            lidx += 1
    return (text, clauses)

def split_clauses(clauses, statives_in_temporal = False):
    refs = []
    temporal = []
    discourse = []
    role = []
    rest = []
    for clause in clauses:
        if re.search(r'b[0-9]+ REF [et][0-9]+', clause):
            refs.append(clause)
        elif re.search(r' [et][0-9]+', clause) and not re.search(r' [xp][0-9]+' if statives_in_temporal else r' [xsp][0-9]+', clause):
            temporal.append(clause)
        elif re.search(r' [et][0-9]+', clause):
            role.append(clause)
        elif re.search(r'b[0-9]+ [A-Z]+ b[0-9]+', clause):
            discourse.append(clause)
        else:
            rest.append(clause)
    return (refs, temporal, discourse, role, rest)

def parse_discourse_clause(clause):
    elements = clause.split()
    boxA = elements[0]
    relation = elements[1]
    boxB = elements[2]
    # if relation in ['CONDITION', 'CONSEQUENCE']:
    #     raise Exception('Can\'t handle discourse relations of type [' + relation + '] yet.')
    # else:
    return (relation, boxA, boxB)

def parse_referent_clause(clause):
    elements = clause.split()
    return (elements[0], elements[2])

def parse_temporal_clause(clause):
    elements = clause.split()
    box = elements[0]
    predicate = elements[1]
    rest = elements[2:]

    rval = []
    sems = []
    if predicate in ['EQU']:
        rval = freksa.e(rest[0], rest[1])
    elif predicate in ['Time']:
        rval = freksa.e(rest[0], rest[1])# + freksa.d(rest[0], rest[1])
    elif predicate.islower() and rest[0].startswith('"v.'):
        sense = predicate + '.' + rest[0].replace('"', '')
        sems = sense_to_semantics(sense)
        for sem in sems:
            sem['args'] = [arg.replace('(E)', '(' + rest[1] + ')') for arg in sem['args']]
        rval = ['|' + predicate + '(' + rest[1] + '),' + rest[1] + '|']
    elif predicate in ['TPR']:
        rval = freksa.b(rest[0], rest[1])
    elif predicate in ['TAB']:
        rval = freksa.m(rest[0], rest[1])
    elif predicate in ['TIN']:
        rval = freksa.d(rest[0], rest[1])
    elif predicate in ['PartOf']:
        rval = freksa.s(rest[0], rest[1]) + freksa.f(rest[0], rest[1])
    elif predicate in ['Stimulus'] and rest[0].startswith('e') and rest[1].startswith('e'):
        rval = ['|' + rest[0] + ',' + rest[1] + ',' + rest[1] + '(' + rest[0] + ')' +'|']
    else:
        rval = []
    return (box, rval, sems)

def list_of_tuples_to_dict(list_of_tuples):
    d = dict()
    for (a, b) in list_of_tuples:
        d.setdefault(a, []).append(b)
    return d

def rel_to_string(relation, a, b):
    #TODO: prevents events and times interacting -> maybe remove
    if a != '' and b != '' and a[0] == b[0] and relation in ['CONTINUATION']:
        return freksa.b(a, b) + freksa.e(a, b)
    if a != '' and b != '' and a[0] == b[0] and relation in ['CONTRAST']:
        return freksa.bi(a, b)
    if relation in ['NEGATION'] and b.startswith('e'):
        # including both positive and negative for superposition's sake
        return ['|' + (a + ',' if a != '' else '') + '¬' + b + ',' + b + '|']
    if relation in ['POSSIBILITY'] and b.startswith('e'):
        # treat this similar to negative
        return ['|' + (a + ',' if a != '' else '') + '?' + b + ',' + b + '|']
    if relation in ['EXPLANATION']:
        return freksa.older(a, b)
    if relation in ['ATTRIBUTION'] and a.startswith('e') and b.startswith('e'):
        return ['|' + a + ',' + b + ',' + b + '(' + a + ')' +'|']
    else:
        return []

#TODO: FIX!!
def compute_transitivities(discourse, deep = False):
    closure = set(discourse)
    shallow_continue = True
    while deep or shallow_continue:
        new_rels = set((r,a,bb) for r,a,b in closure for rr,aa,bb in closure if b == aa)
        # new_rels = set((r,a,bb) for r,a,b in closure for rr,aa,bb in closure if b == aa and r == 'NEGATION')
        updated = closure | new_rels
        if updated == closure:
            break
        closure = updated
        shallow_continue = False
    return list(closure)

def parse_roles(roles):
    elements = roles.split()
    return tuple(elements)

def langs_from_clf(clf):
    (text, clauses) = parse_clf(clf)
    (referent, temporal, discourse, role, _rest) = split_clauses(clauses)
    disc = list(map(parse_discourse_clause, discourse))
    disc = compute_transitivities(disc)
    refs = list_of_tuples_to_dict(list(map(parse_referent_clause, referent)))

    rels = []
    for (rel, boxA, boxB) in disc:
        refsA = refs.get(boxA, [''])
        refsB = refs.get(boxB, [''])
        for refA in refsA:
            for refB in refsB:
                rels.append(rel_to_string(rel, refA, refB))
        
    temp = list(map(parse_temporal_clause, temporal))

    sems = [item for sl in [list(map(sem_to_string, lang[2])) for lang in temp if len(lang[2]) > 0] for item in sl if len(item) > 0]
    
    langs = [lang[1] for lang in temp if len(lang[1]) > 0] + [lang for lang in rels if len(lang) > 0] + sems
    return (text, langs)

def hide_identifiers(string):
    v = vocabulary(string)
    nv = [i for i in v if not re.match(r'^[¬?$]?[bet][0-9]+$', i)]
    return block_compress(reduct(string, nv))

def resolve_effects(string):
    s = string.split('|')
    res = []
    for c in s:
        n = re.search(r'¬(e\d+)', c)
        if n:
            g = n.group(1)
            c = re.sub('\w+\('+g+'\)', '¬\g<0>', c)
        p = re.search(r'\?(e\d+)', c)
        if p:
            g = p.group(1)
            c = re.sub('\w+\('+g+'\)', '?\g<0>', c)
        res.append(c)
    return '|'.join(res)
    


#############################################################
#############################################################

def corpus_crawler(corpus_dir, filename = 'en.drs.clf'):
    result = []
    parts = os.listdir(corpus_dir)
    for part in parts:
        docs = os.listdir(corpus_dir + part)
        for doc in docs:
            result.append(corpus_dir + part + '/' + doc + '/' + filename)
    return result

def predicate_frequencies(corpus, filter_nontemporal = True, no_lowercase = True):
    clauses_per_doc =  map(parse_clf, corpus)
    if filter_nontemporal:
        clauses_per_doc = map(split_clauses, clauses_per_doc)
        clauses_per_doc = map(lambda x: x[0] + x[1] + x[2], clauses_per_doc)
    all_clauses = [clause for doc in clauses_per_doc for clause in doc]
    predicates = list(map(lambda x: x.split()[1] if len(x) > 0 else '', all_clauses))
    if no_lowercase:
        predicates = [predicate for predicate in predicates if not predicate.islower()]
    return collections.Counter(predicates)

def language_length_count(lang_list):
    zero_c = 0
    one_c = 0
    many_c = 0
    for lang in lang_list:
        if len(lang) == 0:
            zero_c += 1
        if len(lang) == 1:
            one_c += 1
        if len(lang) > 1:
            many_c += 1

    # 328 1306 6769
    return {'zero': zero_c, 'one': one_c, 'many': many_c}

def corpus_to_superposed_strings(filenames, start = 0, window = 1, hide_discourse_referents = True):
    languages_list = corpus_to_languages(filenames, start, window)
    findex = start
    
    rval = []
    for (text, lang) in languages_list:
        res = []
        if len(lang) > 0:
            try:
                sps = superpose_all_langs_pick_shortest(lang)
                sps = list(map(resolve_effects, sps))
                res = list(frozenset(map(hide_identifiers, sps) if hide_discourse_referents else sps))
            except Exception as e:
                print('Exception at ' + filenames[findex] + ':')
                print(e)
                break
        rval.append((filenames[findex], lang, res, text))
        findex += 1
    return rval

def corpus_to_languages(filenames, start = 0, window = 1):
    langs = []
    for f in filenames[start:start+window]:
        langs.append(file_to_languages(f))
    return langs

def file_to_languages(filename):
    try:
        return langs_from_clf(filename)
    except Exception as e:
        return ('Exception at ' + filename + ':\n' + str(e), [])

def find_file(part, doc, corpus):
    matching = [f for f in corpus if 'p'+str(part)+'/d'+str(doc) in f]
    if len(matching) == 1:
        return matching[0]

def file_to_id(filename):
    s = re.search(r'p(\d\d)/d(\d\d\d\d)', filename)
    if s:
        return s.groups()
    return filename

#TODO: search forward from 2000 for problem/interesting documents

def print_strings(strings, print_text=False, print_source_strings=False, print_file_ids=False):
    for s in strings:
        f = '/'.join(file_to_id(s[0])) if print_file_ids else ''
        if print_file_ids: print(f)
        if print_text: print(s[3])
        if print_source_strings: print(s[1])
        print(s[2])
        # if print_file_ids: print(f)
        print()

################

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(prog='pmb-parse')


    arg_parser.add_argument('-c', '--corpus_path', default='/home/david/pgrad/PMB-analysis/pmb-3.0.0/data/en/gold/', help='Set the corpus\' path for the corpus_* subcommands')
    arg_parser.add_argument('-f', '--file_path', help='Produce strings for a specific file, given its path')
    arg_parser.add_argument('--show_referents', action='store_true', help='Display discourse referents when producing strings')
    arg_parser.add_argument('--print_text', action='store_true', help='Display the source text when printing strings')
    arg_parser.add_argument('--print_src', action='store_true', help='Display the source clause-strings when printing strings')
    arg_parser.add_argument('--print_ids', action='store_true', help='Display file ids when printing strings')

    subparsers = arg_parser.add_subparsers(dest='subparser_name')

    f_parser = subparsers.add_parser('corpus_file', help='Specify a file from the corpus by its part and document ids, and produce strings from it')
    c_parser = subparsers.add_parser('corpus_slice', help='Produce strings for a number of files from the corpus')
    q_parser = subparsers.add_parser('corpus_freq', help='Show the frequency of each predicate in the corpus')
    c_parser.add_argument('slice_start_index', nargs='?', default=0, type=int, help='Set the index of the first file in the slice. NB: corpus order is not guaranteed')
    c_parser.add_argument('slice_window_size', nargs='?', default=10, type=int, help='Set the size of the slice')
    f_parser.add_argument('part', help='The numeric part id (two digits)')
    f_parser.add_argument('document', help='The numeric document id (four digits)')
    q_parser.add_argument('--include_nontemporal', action='store_true')
    q_parser.add_argument('--include_lowercase', action='store_true')

    args = arg_parser.parse_args()

    hdr = not args.show_referents

    if args.file_path:
        strings = corpus_to_superposed_strings([args.file_path], 0, 1, hdr)
        print_strings(strings, args.print_text, args.print_src)
    else:
        corpus = corpus_crawler(args.corpus_path)
        if args.subparser_name == 'corpus_file':
            f = find_file(args.part, args.document, corpus)
            strings = corpus_to_superposed_strings([f], 0, 1, hdr)
            print_strings(strings, args.print_text, args.print_src, args.print_ids)
        elif args.subparser_name == 'corpus_slice':
            strings = corpus_to_superposed_strings(corpus, args.slice_start_index, args.slice_window_size, hdr)
            print_strings(strings, args.print_text, args.print_src, args.print_ids)
        elif args.subparser_name == 'corpus_freq':
            exc_nt = not args.include_nontemporal
            exc_lc = not args.include_lowercase
            cc = predicate_frequencies(corpus, exc_nt, exc_lc)
            print(dict(cc))

################