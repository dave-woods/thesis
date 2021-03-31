import strfns
import json
import sys

def string_to_rel(string, x):
    t, m = strfns.analogous_strings(string, '|X||Y|')
    if t:
        return 'BEFORE' if m[x] == 'X' else 'AFTER'
    t, m = strfns.analogous_strings(string, '|X|Y|')
    if t:
        return 'IBEFORE' if m[x] == 'X' else 'IAFTER'
    t, m = strfns.analogous_strings(string, '|X,Y|')
    if t:
        return 'SIMULTANEOUS'
    t, m = strfns.analogous_strings(string, '|X|X,Y|X|')
    if t:
        return 'INCLUDES' if m[x] == 'X' else 'DURING'
    t, m = strfns.analogous_strings(string, '|X|X,Y|')
    if t:
        return 'ENDED_BY' if m[x] == 'X' else 'ENDS'
    t, m = strfns.analogous_strings(string, '|X,Y|X|')
    if t:
        return 'BEGUN_BY' if m[x] == 'X' else 'BEGINS'
    t, m = strfns.analogous_strings(string, '|X|X,Y|Y|')
    if t:
        return 'OVERLAPS' if m[x] == 'X' else 'OVERLAPPED_BY'
    return 'UNKNOWN'+string


if __name__ == "__main__" and len(sys.argv) - 1 == 1:
    passed_data = json.loads(sys.argv[1])
    try:
        vocab = passed_data['vocabulary']
        strings = None
        try:
            strings = frozenset(strfns.flatten_list(strfns.superpose_all_langs_sensible(passed_data['strings'], 12)))
        except:
            strings = frozenset(strfns.flatten_list(passed_data['strings']))
        idx = 0
        lid = 0
        result = []
        for v in vocab:
            for w in vocab[idx+1:]:
                p = strfns.projection_lang_full_vocab(strings, [v, w])
                if len(p) > 0:
                    r = '|'.join(map(lambda s: string_to_rel(s, v), p))
                    result.append('<TLINK lid="{0}" {1}="{2}" {3}="{4}" relType="{5}" />'.format(lid, 'eventID' if v[0] == 'e' else 'timeID', v, 'relatedToEvent' if w[0] == 'e' else 'relatedToTime', w, r))
                    lid += 1
            idx += 1
        print(json.dumps(result), end='')
    except Exception as e:
        print(e, end='', file=sys.stderr)
