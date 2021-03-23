import wsf
import freksa
import json
import sys

ll = json.loads(sys.argv[1])
try:
    kb = ll['strings']
    test_strings = getattr(freksa, ll['rel'])(ll['e1'], ll['e2'])
    result = dict()
    result['strings'] = test_strings
    result['status'] = 'contradicted'
    if not any(any(wsf.lang_contradicts_string(lang, ts) for lang in kb) for ts in test_strings):
        result['status'] = 'possible'
        if any(any(wsf.lang_contains_string(lang, ts) for lang in kb) for ts in test_strings):
            result['status'] = 'found'

    print(json.dumps(result), end='')
except Exception as e:
    print(e, end='', file=sys.stderr)
