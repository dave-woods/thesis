import wsf
import json
import sys

ll = json.loads(sys.argv[1])
print(json.dumps(list(wsf.superpose_all_langs_sensible(ll, 13))), end='')
