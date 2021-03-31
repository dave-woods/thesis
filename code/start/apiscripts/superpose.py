import strfns
import json
import sys

if __name__ == "__main__" and len(sys.argv) - 1 == 1:
    passed_data = json.loads(sys.argv[1])
    try:
        print(json.dumps(list(strfns.superpose_all_langs_sensible(passed_data['strings'], passed_data['limit']))), end='')
    except Exception as e:
        print(e, end='', file=sys.stderr)
