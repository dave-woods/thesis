from string_functions import superpose_all_langs,superpose_all_langs_gen,string_length,delete_empty_boxes,reduct,vocabulary,hide_negated,get_components,superpose_all_langs_pick_shortest
from functools import partial
import re

def permute(items):
    return ['|'.join(i) for i in itertools.permutations(items)]


def border_box_variants(string):
    components = get_components(string)
    return ['{}|{}'.format(negate_component(components[0], True), string), '{}|{}'.format(string, negate_component(components[-1], True)), '{}|{}|{}'.format(negate_component(components[0], True), string, negate_component(components[-1], True))]

from zebra_clue_parser import parser

cluefile = 'zebra-puzzle-clues.txt'
clues = parser(cluefile)
types = clues[0]

preconds = lambda fns: partial(lambda s: all(fn(s) for fn in fns))
pcx1 = partial(lambda s: string_length(s) == 5) # five houses
pcx2 = partial(lambda s: all(string_length(delete_empty_boxes(reduct(hide_negated(s), [v]))) == 1 for v in vocabulary(s))) # each item is in one house
pcx3 = partial(lambda s: all(all(len(re.findall(r'{}\([^)]+?\)'.format(t), c)) < 2 for t in types) for c in hide_negated(s).split('|'))) # each house has one item

sp = superpose_all_langs_pick_shortest(clues[1], preconds([pcx1, pcx2, pcx3]))
for s in sp:
    print(hide_negated(s))

