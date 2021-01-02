from functools import reduce
from collections import Counter
import re

class String(object):
    def __init__(self, _string, _label=''):
        if isinstance(_string, String):
            self.string = _string.string
            self.boxes = _string.boxes
        elif isinstance(_string, str):
            self.string = _string.replace(' ', '')
            self.boxes = String.get_boxes(self.string)
        elif isinstance(_string, list):
            self.boxes = _string
            self.string = '|'.join([','.join(b) for b in self.boxes])
        else:
            raise TypeError('String can only be initialised from either a string or a list of boxes.')
        self.substrings = {}
        self.vocabulary = String.get_vocabulary(self.boxes)
        self.length = len(self.boxes)
        self.label = _label

    #region hidden methods
    def __str__(self):
        return self.string

    def __repr__(self):
        return '\'{}\''.format(self.string)

    def __iter__(self):
        return iter(self.boxes)

    def __getitem__(self, key):
        try:
            return self.boxes[key]
        except TypeError as e:
            print('TypeError: Cannot index {} using \'{}\', {}'.format(self, key, e))

    def __and__(self, other):
        return self.superpose(other)

    def __len__(self):
        return self.length

    def __eq__(self, other):

        return isinstance(self, String) and isinstance(other, String) and self.string == other.string
    
    def __ne__(self, other):
        return not isinstance(self, String) or not isinstance(other, String) or self.string != other.string

    def __hash__(self):
        return hash(self.string)

    def concat(self, other):
        return String(self.boxes + other.boxes)

    def __add__(self, other):
        return self.concat(other)
    #endregion classmethods

    def set_label(self, label):
        self.label = label

    @staticmethod
    def get_boxes(string):
        return [s.split(',') for s in string.replace(' ', '').split('|')]

    @staticmethod
    def get_vocabulary(boxes):
        if len(boxes) == 0:
            return []
        return list(filter(None, reduce(lambda x, y: list(frozenset(x) | frozenset(y)), boxes)))

    @staticmethod
    def negate_fluent(fluent):
        return fluent[1:] if fluent == '' or fluent.startswith('!') else '!'+fluent

    @staticmethod
    def negate_box(box):
        return list(map(String.negate_fluent, box))

    def negate(self):
        return String(list(map(String.negate_box, self.boxes)))

    def hide_negation(self):
        return String(list(map(lambda b: list(filter(lambda f: not f.startswith('!'), b)), self.boxes)))

    def all_P(self, fluent):
        for x in range(self.length):
            if self.P(fluent, x):
                yield x

    def P(self, f, x):
        try:
            return f in self.boxes[x] or (f.startswith('!') and String.negate_fluent(f) not in self.boxes[x])
        except IndexError:
            return False
    
    def contains(self, f):
        return not not list(self.all_P(f))

    def define_substring(self, name, start=None, end=None):
        if name in self.substrings.keys():
            raise Exception('The substring \'{}\' already exists'.format(name))
        else:
            self.substrings[name] = (start, end, String(self.boxes[start:end]))

    def display_substrings(self):
        ss = []
        for k, v in self.substrings.items():
            start = v[0] if v[0] is not None else 0
            end = v[1] if v[1] is not None else self.length
            s = String(self[:start] + [[k]] + self[end:])
            print(s)
            ss.append(s)
        return ss

    def remove_substring(self, name):
        del self.substrings[name]

    @staticmethod
    def list_as_language(l):
        return Language(l)

    @staticmethod
    def __nonempty_union(x, y):
        try:
            z = frozenset(x) | frozenset(y)
        except:
            z = x + y
        return list(filter(None, z)) if len(z) > 1 else list(z)

    @staticmethod
    def __L(s1, s2, v1, v2, string_filter):
        t1 = String(s1[1:])
        t2 = String(s2[1:])
        p1 = list(s1.superpose(t2, v1, v2, string_filter))
        p2 = list(t1.superpose(s2, v1, v2, string_filter))
        p3 = list(t1.superpose(t2, v1, v2, string_filter))
        # Look into using the multiprocessing module for the above, but issues
        # arise due to invisible pickling of the superpose generators
        return String.__nonempty_union(String.__nonempty_union(p1, p2), p3)

    def superpose(self, other, v1=None, v2=None, string_filter=None):
        if isinstance(other, str):
            yield from self.superpose(String(other), v1, v2, string_filter)
        else:
            if v1 is None and v2 is None:
                v1 = self.vocabulary
                v2 = other.vocabulary
            if self.length == 0 and other.length == 0:
                yield []
            elif self.length == 0 or other.length == 0:
                yield []
            elif frozenset(v1) & frozenset(other.boxes[0]) <= frozenset(self.boxes[0]) and frozenset(v2) & frozenset(self.boxes[0]) <= frozenset(other.boxes[0]):
                head_union = self.__nonempty_union(self.boxes[0], other.boxes[0])
                r = []
                for l in String.__L(self, other, v1, v2, string_filter):
                    try:
                        s = String([head_union] + l.boxes)
                    except AttributeError:
                        s = String([head_union] + l)
                    if string_filter is None or string_filter(s):
                        r.append(s)
                yield from r
            else:
                yield []

    @staticmethod
    def superpose_all(list_of_strings, string_filter=None):
        if type(list_of_strings) != list:
            raise TypeError('argument must be of type list, not type {}'.format(list_of_strings.__class__.__name__))
        elif len(list_of_strings) == 0:
            raise Exception('Cannot use empty list')
        elif len(list_of_strings) == 1:
            yield list_of_strings[0]
        else:
            try:
                first_pair = list_of_strings[0].superpose(list_of_strings[1], string_filter)
            except AttributeError:
                first_pair = String(list_of_strings[0]).superpose(list_of_strings[1], string_filter)
            for sp in first_pair:
                yield from String.superpose_all([sp] + list_of_strings[2:], string_filter)

    @staticmethod
    def from_borders(border_string):
        ns = [['']]
        for i, b in enumerate(border_string):
            app = False
            if i < border_string.length - 1:
                app = True
                ns.append(ns[i])
            for f in b:
                m = re.match(r'l\(([^)]+)\)', f)
                if m:
                    if not app:
                        app = True
                        ns.append(ns[i])
                    if ns[i+1][0] == '':
                        ns[i+1] = [m.groups()[0]]
                    else:
                        ns[i+1] = ns[i+1] + [m.groups()[0]]
                else:
                    m = re.match(r'r\(([^)]+)\)', f)
                    if m:
                        mg = m.groups()[0]
                        if mg not in ns[i]:
                            ns[i] = [n for n in ns[i] if n != ''] + [mg]
                        if mg in ns[i+1]:
                            ns[i+1] = [n for n in ns[i+1] if n != mg]
                            if len(ns[i+1]) == 0:
                                ns[i+1] = ['']
        return String(ns)


    @staticmethod
    def to_borders(string):
        s1 = string
        ns = []
        for i, b in enumerate(s1):
            nb = []
            if i == s1.length - 1:
                pass
            else:
                for f in s1[i+1]:
                    if f != '' and f not in b:
                        nb.append('l({})'.format(f))
                for f in b:
                    if f != '' and f not in s1[i+1]:
                        nb.append('r({})'.format(f))
            ns.append(nb if len(nb) > 0 else [''])
        return String(ns)

    def block_compress(self):
        if self.length < 2:
            return self
        elif Counter(self.boxes[0]) == Counter(self.boxes[1]):
            return String(self.boxes[1:]).block_compress()
        else:
            return String([self.boxes[0]] + String(self.boxes[1:]).block_compress().boxes)

    def reduct(self, new_vocab):
        return String([[f for f in b if f in new_vocab] for b in self.boxes])

    def projects(self, other):
        return self.reduct(other.vocabulary).block_compress() == other

    def delete_empty_boxes(self):
        return String([b for b in self.boxes if b not in [[None], [], ['']]])

    def pad_left(self, pad_by=1, pad_with=['']):
        return String([pad_with]*pad_by+self.boxes)
    
    def pad_right(self, pad_by=1, pad_with=['']):
        return String(self.boxes + [pad_with]*pad_by)

    def pad_both(self, pad_by=1, pad_with=['']):
        return self.pad_left(pad_by, pad_with).pad_right(pad_by, pad_with)

class Language(object):
    def __init__(self, plang=[], lang_filter=None):
        try:
            if isinstance(plang, list):
                self.lang = list(filter(lang_filter, set(map(String, plang))))
            elif isinstance(plang, Language):
                self.lang = list(filter(lang_filter, set(map(String, plang.lang))))
            else:
                self.lang = []
        except TypeError:
            self.lang = []
            print('One or more items in the argument could not be converted to a String')

    #region hidden methods
    def __add__(self, other):
        try:
            return Language(self.lang + other.lang)
        except AttributeError:
            return Language(self.lang + Language(other).lang)

    def __repr__(self):
        return str(self.lang)

    def __iter__(self):
        return iter(self.lang)

    def __getitem__(self, key):
        try:
            return self.lang[key]
        except TypeError as e:
            print('TypeError: Cannot index {} using \'{}\', {}'.format(self, key, e))

    def __and__(self, other):
        return self.superpose(other)

    def __len__(self):
        return len(self.lang)
    #endregion hidden methods

    def superpose(self, other, lang_filter=None, string_filter=None):
        for s1 in self.lang:
            for s2 in other.lang:
                for s in s1.superpose(s2, string_filter):
                    if lang_filter is None or lang_filter(s):
                        yield s

    @staticmethod
    def superpose_all(list_of_langs, lang_filter=None, string_filter=None):
        if type(list_of_langs) != list:
            raise TypeError('argument must be of type list, not type {}'.format(list_of_langs.__class__.__name__))
        elif len(list_of_langs) == 0:
            raise Exception('Cannot use empty list')
        elif len(list_of_langs) == 1:
            yield from list_of_langs[0]
        else:
            first_pair = list_of_langs[0].superpose(list_of_langs[1], lang_filter, string_filter)
            yield from Language.superpose_all([Language(first_pair)] + list_of_langs[2:], lang_filter, string_filter)

    @staticmethod
    def from_lists(l):
        return list(map(Language, l))
     