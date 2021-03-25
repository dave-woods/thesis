import wsf
import json
import sys

#  BEFORE: 'b',
#  AFTER: 'bi',
#  INCLUDES: 'di',
#  DURING_INV: 'di',
#  IS_INCLUDED: 'd',
#  DURING: 'd',
#  SIMULTANEOUS: 'e',
#  IDENTITY: 'e',
#  IAFTER: 'mi',
#  IBEFORE: 'm',
#  BEGINS: 's',
#  ENDS: 'f',
#  BEGUN_BY: 'si',
#  ENDED_BY: 'fi'

def string_to_rel(string, x):
    t, m = wsf.analogous_strings(string, '|X||Y|')
    if t:
        return 'BEFORE' if m[x] == 'X' else 'AFTER'
    t, m = wsf.analogous_strings(string, '|X|Y|')
    if t:
        return 'IBEFORE' if m[x] == 'X' else 'IAFTER'
    t, m = wsf.analogous_strings(string, '|X,Y|')
    if t:
        return 'SIMULTANEOUS'
    t, m = wsf.analogous_strings(string, '|X|X,Y|X|')
    if t:
        return 'INCLUDES' if m[x] == 'X' else 'DURING'
    t, m = wsf.analogous_strings(string, '|X|X,Y|')
    if t:
        return 'ENDED_BY' if m[x] == 'X' else 'ENDS'
    t, m = wsf.analogous_strings(string, '|X,Y|X|')
    if t:
        return 'BEGUN_BY' if m[x] == 'X' else 'BEGINS'
    t, m = wsf.analogous_strings(string, '|X|X,Y|Y|')
    if t:
        return 'OVERLAPS' if m[x] == 'X' else 'OVERLAPPED_BY'
    return 'UNKNOWN'+string

ll = json.loads(sys.argv[1])
try:
    vocab = ll['vocabulary']
    strings = frozenset(wsf.flatten_list(ll['strings']))
    idx = 0
    lid = 0
    result = []
    for v in vocab:
        for w in vocab[idx+1:]:
            p = wsf.projection_lang_full_vocab(strings, [v, w])
            if len(p) > 0:
                r = '|'.join(map(lambda s: string_to_rel(s, v), p))
                result.append('<TLINK lid="{0}" {1}="{2}" {3}="{4}" relType="{5}" />'.format(lid, 'eventID' if v[0] == 'e' else 'timeID', v, 'relatedToEvent' if w[0] == 'e' else 'relatedToTime', w, r))
                lid += 1
        idx += 1
    print(json.dumps(result), end='')
except Exception as e:
    print(e, end='', file=sys.stderr)
