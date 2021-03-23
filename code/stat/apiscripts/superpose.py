import wsf
import json
import sys

ll = json.loads(sys.argv[1])
try:
    print(json.dumps(list(wsf.superpose_all_langs_sensible(ll['strings'], ll['limit']))), end='')
except Exception as e:
    print(e, end='', file=sys.stderr)
