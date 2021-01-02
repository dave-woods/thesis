import nltk

from nltk.corpus import wordnet as wn
from nltk.corpus import verbnet as vn

import re

import freksa

__internal_event_index = 0

def sense_to_semantics(sense, print_steps=False):
    synset = wn.synset(sense)
    if print_steps: print(synset)
    lemmas = synset.lemmas()
    if print_steps: print(lemmas)
    # assume first item for all the below since we don't have further clarification
    key = lemmas[0].key().rstrip(':')
    if print_steps: print(key)
    vclasses = vn.classids(wordnetid=key)
    if print_steps: print(vclasses)
    if len(vclasses) < 1:
        return
    v = vn.vnclass(vclasses[0])
    f = v.find('FRAMES')
    s = f[0].find('SEMANTICS')
    sem = []
    for pred in s:
        p = pred.get('value')
        if pred.get('bool') == '!':
            p = '¬' + p
        args = pred.find('ARGS')
        a = [arg.get('value') for arg in args]
        sem.append({'pred': p, 'args': a})
    return sem

def sem_to_string(sem):
    global __internal_event_index
    __internal_event_index += 1
    rel = 'un'
    eid = 'e?'
    s = re.search(r'(\w+)\(([et]\d+)\)', sem['args'][0])
    if s:
        rel = s.group(1)
        eid = s.group(2)
    ss = sem['pred'] + '($e' + str(__internal_event_index) +  ')<' + ';'.join(sem['args'][1:]) + '>,$e' + str(__internal_event_index) + '(' + eid + '),$e' + str(__internal_event_index)
    if rel == 'during':
        return freksa.during(ss, eid)
    if rel == 'start':
        return freksa.meets(ss, eid)
    if rel == 'end':
        return freksa.meets_inv(ss, eid)
    try:
        return []
        # return getattr(freksa, rel)(ss, eid)
    except Exception as err:
        print(err)
        return []

def print_semantics(sem):
    for predicate in sem:
        print(predicate['pred'] + '(' + ', '.join(predicate['args']) + ')')

    # frames = vn.frames(vclasses[0])
    # semantics = frames[0]['semantics']
    # print(semantics)
    # for e in semantics:
    #     print(e['predicate_value'], list(map(lambda x: x['value'], e['arguments'])))


if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(prog='net-analyser')

    arg_parser.add_argument('verbsense')
    arg_parser.add_argument('--steps', action='store_true')

    cmd_args = arg_parser.parse_args()

    if cmd_args.verbsense:
        s = sense_to_semantics(cmd_args.verbsense, cmd_args.steps)
        print_semantics(s)
