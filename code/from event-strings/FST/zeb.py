from fst import String, Language
from functools import partial
import re

def border_box_variants(string):
    if isinstance(string, str):
        string = String(string)
    return Language([
        string.pad_left(1,String.negate_box(string[0])),
        string.pad_right(1,String.negate_box(string[-1])),
        string.pad_left(1,String.negate_box(string[0])).pad_right(1,String.negate_box(string[-1]))
    ])

types = ['nat', 'col', 'dri', 'smo', 'pet']

preconditions = lambda fns: lambda s: all(fn(s) for fn in fns)

pc1 = lambda s: len(s) == 5 # five houses
pc2 = lambda s: all(s.hide_negation().reduct([v]).delete_empty_boxes().length == 1 for v in s.hide_negation().vocabulary) # each item is in one house
pc3 = lambda s: all(all(len(re.findall(r'{}\([^)]+?\)'.format(t), ','.join(c))) < 2 for t in types) for c in s.hide_negation().components) # each house has one item


c1 = Language(['1|2|3|4|5'])
c2 = border_box_variants('nat(eng),col(red)')
c3 = border_box_variants('nat(spa),pet(dog)')
c4 = border_box_variants('dri(cof),col(gre)')
c5 = border_box_variants('dri(tea),nat(ukr)')
c6 = border_box_variants('col(ivo)|col(gre)')
c7 = border_box_variants('smo(old),pet(sna)')
c8 = border_box_variants('smo(koo),col(yel)')
c9 = Language(['1|2|3,dri(mil)|4|5'])
c10 = Language(['1,nat(nor)|2|3|4|5'])
c11 = border_box_variants('smo(che)|pet(fox)') + border_box_variants('pet(fox)|smo(che)')
c12 = border_box_variants('smo(koo)|pet(hor)') + border_box_variants('pet(hor)|smo(koo)')
c13 = border_box_variants('smo(luc),dri(ora)')
c14 = border_box_variants('nat(jap),smo(par)')
c15 = border_box_variants('nat(nor)|col(blu)') + border_box_variants('col(blu)|nat(nor)')