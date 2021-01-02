from os import walk as os_walk
from itertools import product as iter_product

import settings
import string_functions_old
superpose = string_functions_old.superpose
pw_sp = string_functions_old.pw_sp
vocab = string_functions_old.vocabulary

# increasing this will reduce the number of final non-deterministic partial timelines, but increases the level of non-determinism, and thus the complexity and processing time.
MAX_LANGUAGE_SIZE = 0


def get_corpus_filenames(corpus_directory):
    _, _, files = list(os_walk(corpus_directory))[0] # seems hacky, but does the job
    return files

def string_sorter(input_strings, remove_self_referents = True):
    strings = input_strings.copy()
    for index, string in enumerate(strings):
        vocab_s = vocab(string)
        if remove_self_referents and len(vocab_s) == 1:
            strings[index] = '-'
            continue
        for index_2, string_2 in enumerate(strings[index + 1:]):
            if index_2 == 0:
                continue
            if [val for val in vocab_s if val in vocab(string_2)]:
                strings.insert(index + 1, strings.pop(index + 1 + index_2))
    if remove_self_referents:
        return list(filter(lambda x: x != '-', strings))
    return strings

def run_pw_superposition(input_strings):
    "run pointwise superposition"
    strings = input_strings.copy()
    for i in range(len(strings) - 1):
        j = i + 1
        if isinstance(strings[i], str):
            vocab_a = vocab(strings[i])
            vocab_b = vocab(strings[j])
            if [val for val in vocab_a if val in vocab_b]:
                sp = pw_sp(strings[i], strings[j])
                if not sp:
                    settings.issue_found(3, 'WARNING: Empty result from superposition.\nInconsistency between {0} and {1}.'.format(strings[i], strings[j]))
                strings[j] = sp
                strings[i] = '-'
        else:
            vocab_a = vocab(strings[i][0])
            vocab_b = vocab(strings[j])
            if [val for val in vocab_a if val in vocab_b]:
                l = [pw_sp(s, strings[j]) for s in strings[i]]
                sp = [item for sublist in l if sublist for item in sublist]
                if not sp:
                    settings.issue_found(3, 'WARNING: Empty result from superposition.\nInconsistency between {0} and {1}.'.format(strings[i], strings[j]))
                if sp and len(sp) <= MAX_LANGUAGE_SIZE:
                    strings[j] = sp
                    strings[i] = '-'
    return strings

def run_superposition(input_strings):
    strings = input_strings.copy()
    for i in range(len(strings) - 1):
        j = i + 1
        if isinstance(strings[i], str):
            vocab_a = vocab(strings[i])
            vocab_b = vocab(strings[j])
            if [val for val in vocab_a if val in vocab_b]:
                sp = superpose(strings[i], strings[j])
                if not sp:
                    settings.issue_found(3, 'WARNING: Empty result from superposition.\nInconsistency between {0} and {1}.'.format(strings[i], strings[j]))
                strings[j] = sp
                strings[i] = '-'
        else:
            vocab_a = vocab(strings[i][0])
            vocab_b = vocab(strings[j])
            if [val for val in vocab_a if val in vocab_b]:
                l = [superpose(s, strings[j]) for s in strings[i]]
                sp = [item for sublist in l if sublist for item in sublist]
                if not sp:
                    settings.issue_found(3, 'WARNING: Empty result from superposition.\nInconsistency between {0} and {1}.'.format(strings[i], strings[j]))
                if sp and (MAX_LANGUAGE_SIZE == 0 or len(sp) <= MAX_LANGUAGE_SIZE):
                    strings[j] = sp
                    strings[i] = '-'
    return strings
