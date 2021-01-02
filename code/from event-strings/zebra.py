from string_functions import permute,border_box_variants,superpose_all_langs,superpose_all_langs_gen,string_length,delete_empty_boxes,reduct,vocabulary,hide_negated,get_components,superpose_all_langs_pick_shortest
from functools import partial
import re

from zebra_clue_parser import parser

# pc1 = permute(['nat(eng)','nat(spa)','nat(nor)','nat(ukr)','nat(jap)'])
# pc2 = permute(['col(red)','col(ivo)','col(yel)','col(blu)','col(gre)'])
# pc3 = permute(['dri(wat)','dri(tea)','dri(mil)','dri(cof)','dri(ora)'])
# pc4 = permute(['smo(koo)','smo(che)','smo(old)','smo(luc)','smo(par)'])
# pc5 = permute(['pet(fox)','pet(hor)','pet(sna)','pet(dog)','pet(zeb)'])

cluefile = 'zebra-puzzle-clues.txt'
clues = parser(cluefile)
types = clues[0]

preconds = lambda fns: partial(lambda s: all(fn(s) for fn in fns))
pcx1 = partial(lambda s: string_length(s) == 5) # five houses
pcx2 = partial(lambda s: all(string_length(delete_empty_boxes(reduct(hide_negated(s), [v]))) == 1 for v in vocabulary(s))) # each item is in one house
pcx3 = partial(lambda s: all(all(len(re.findall(r'{}\([^)]+?\)'.format(t), c)) < 2 for t in types) for c in hide_negated(s).split('|'))) # each house has one item

# sp = superpose_all_langs(clues[1], preconds([pcx1, pcx2, pcx3]))
# for s in sp:
#     print(hide_negated(s))

sp = superpose_all_langs_pick_shortest(clues[1], preconds([pcx1, pcx2, pcx3]))
for s in sp:
    print(hide_negated(s))

# sp = superpose_all_langs_gen(clues[1], preconds([pcx1, pcx2, pcx3]))
# for item in sp:
#     idx = 1
#     for s in item:
#         print(idx, '---', hide_negated(s))
#         idx += 1
#     input('\n\r[Press Enter to continue]\n\r')

# import timeit
# t1 = timeit.timeit(lambda: superpose_all_langs(clues[1], preconds([pcx1, pcx2, pcx3])), number=100)
# print('default', t1, t1/100)
# t2 = timeit.timeit(lambda: superpose_all_langs_pick_shortest(clues[1], preconds([pcx1, pcx2, pcx3])), number=100)
# print('pick', t2, t2/100)

# pc1 = permute(['eng', 'jap', 'spa'])
# pc2 = permute(['red', 'gre', 'blu'])
# pc3 = permute(['zeb', 'jag', 'sna'])
# pc4 = partial(lambda s: string_length(s) == 3)
# s1 = border_box_variants('red,eng')
# s2 = border_box_variants('jag,spa')
# s3 = border_box_variants('sna|jap')
# s4 = border_box_variants('sna|blu')
