import strfns
import freksa
import json
import sys

if __name__ == "__main__" and len(sys.argv) - 1 == 1:
    passed_data = json.loads(sys.argv[1])
    try:
        kb = passed_data['strings']
        test_strings = getattr(freksa, passed_data['rel'])(passed_data['e1'], passed_data['e2'])
        result = dict()
        result['strings'] = test_strings
        result['status'] = 'contradicted'
        if not any(any(strfns.lang_contradicts_string(lang, ts) for lang in kb) for ts in test_strings):
            result['status'] = 'possible'
            if any(any(strfns.lang_contains_string(lang, ts) for lang in kb) for ts in test_strings):
                result['status'] = 'found'

        print(json.dumps(result), end='')
    except Exception as e:
        print(e, end='', file=sys.stderr)
