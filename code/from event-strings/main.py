import sys
import re
from subprocess import call, STDOUT
from functools import reduce
from os import devnull

import settings
import timeml_parser
import corpus_checker
import string_functions_old

# Adjust to 'ALL' to get warnings+errors
settings.init(log_level='INFO')

def check_corpus(files = []):
    timeml_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
    if not files:
        corpus = corpus_checker.get_corpus_filenames(timeml_dir)
    else:
        corpus = files
    with open('timebank-reduction-counts.txt', 'w') as printfile:
        printfile.write('corpusfile,num_events,num_tlinks,num_timelines,problem_found\n')
        for corpus_file in corpus:
            settings.__issue_found = None
            doc = timeml_parser.get_document_root(timeml_dir + corpus_file)
            tlinks = timeml_parser.get_tlinks(doc)
            strings = timeml_parser.tlinks_to_strings(tlinks)
            s1 = strings.copy()
            s2 = corpus_checker.string_sorter(s1, True)
            s3 = corpus_checker.run_superposition(s2)
            event_list = sorted(reduce(lambda x, y: string_functions_old.nonempty_union(x, string_functions_old.vocabulary(y)), s2, []))
            event_list_length = len(event_list)
            strings_length = len(s2)
            timelines_length = len(list(filter(lambda x: x != '-', s3)))
            printfile.write('{},{},{},{},{}\n'.format(corpus_file, event_list_length, strings_length, timelines_length, settings.__issue_found))
        printfile.close()
        print('done')

def get_minimal_substrings(filename, print_timelines = True):
    timeml_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
    doc = ''
    try:
        doc = timeml_parser.get_document_root(filename)
    except FileNotFoundError:
        try:
            doc = timeml_parser.get_document_root(timeml_dir + filename)
        except FileNotFoundError:
            print('File {} does not seem to exist in either the local directory or the corpus'.format(filename))
            return
    tlinks = timeml_parser.get_tlinks(doc)
    strings = timeml_parser.tlinks_to_strings(tlinks)
    s1 = strings.copy()
    s2 = corpus_checker.string_sorter(s1, True)
    s3 = corpus_checker.run_superposition(s2)
    timelines = list(filter(lambda x: x != '-', s3))
    if (print_timelines):
        count = 0
        for tl in timelines:
            if isinstance(tl, str):
                count += 1
                print('* {}'.format(tl))
            elif isinstance(tl, list):
                count += len(tl)
                print('* {}'.format('; '.join(tl)))
        print('length:', count)
    return timelines

def output_text(infile, outfile = None):
    if not outfile:
        m = re.search(r'^(.*)\.tml$', infile)
        outfile = '{}.txt'.format(m.group(1))
    doc = timeml_parser.get_document_root(infile)
    with open(outfile, 'w') as printfile:
        text = timeml_parser.get_text(doc)
        text = re.sub('(?<=[^.])\n{1}(?=[^\n]+)', ' ', text)
        printfile.write(text)

def examine_output():
    import csv
    with open('timebank-reduction-counts.txt', 'r') as readfile:
        reader = csv.reader(readfile)
        # headers = next(reader, None)
        # print(headers)
        for index, row in enumerate([r for r in reader if r[4] != 'None']):
            print(index, row)
        readfile.close()

def other_stuff():
    timeml_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
    corpus = corpus_checker.get_corpus_filenames(timeml_dir)
    for corpus_file in corpus:
        doc = timeml_parser.get_document_root(timeml_dir + corpus_file)
        t = list(map(lambda x: x.attrib['tid'], timeml_parser.get_timexs(doc)))
        i = list(map(lambda x: x.attrib['eiid'], timeml_parser.get_instances(doc)))
        el = sorted(reduce(lambda x, y: string_functions_old.nonempty_union(x, string_functions_old.vocabulary(y)), timeml_parser.tlinks_to_strings(timeml_parser.get_tlinks(doc)), []))
        # eq = (len(t) + len(i)) == len(el)

        print(corpus_file, (frozenset(t) | frozenset(i)) - frozenset(el))
        
def tml_to_box(infile, preserve_intermediaries = False):
    timeml_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
    tools = '/home/david/Downloads/candcboxer/'
    tokeniser = 'bin/tokkie'
    parser = 'bin/candc'
    model = 'models/boxer'
    boxer = 'bin/boxer'
    with open(devnull, 'w') as FNULL:
        try:
            m = re.search(r'^(.*)\.tml$', infile)
            fname = m.group(1)
            
            outfile = '{}.txt'.format(fname)
            print('Getting text...')
            try:
                doc = timeml_parser.get_document_root(infile)
            except FileNotFoundError:
                try:
                    doc = timeml_parser.get_document_root(timeml_dir + infile)
                except FileNotFoundError:
                    print('File {} does not seem to exist in either the local directory or the corpus'.format(infile))
                    return
            text = timeml_parser.get_text(doc)
            text = re.sub('(?<=[^.])\n{1}(?=[^\n]+)', ' ', text)
            with open(outfile, 'w') as printfile:
                printfile.write(text)

            infile = outfile
            outfile = '{}.tok'.format(fname)
            print('Tokenising...')
            call([tools + tokeniser, '--input', infile, '--output', outfile], stdout=FNULL, stderr=STDOUT)

            infile = outfile
            outfile = '{}.ccg'.format(fname)
            print('Parsing with CCG...')
            call([tools + parser, '--input', infile, '--models', tools + model, '--candc-printer', 'boxer', '--output', outfile], stdout=FNULL, stderr=STDOUT)

            infile = outfile
            outfile = '{}.drs'.format(fname)
            print('Boxing...')
            call([tools + boxer, '--input', infile, '--box', '--roles', 'verbnet','--resolve', '--semantics', 'sdrs', '--output', outfile], stdout=FNULL, stderr=STDOUT)

            if not preserve_intermediaries:
                call(['rm', '{}.txt'.format(fname)])
                call(['rm', '{}.tok'.format(fname)])
                call(['rm', '{}.ccg'.format(fname)])
            print('Done. Saved to {}.drs'.format(fname))
        except Exception as e:
            print('Something went wrong. :(')
            print(e)

        
    # import nltk
    # text = timeml_parser.get_text(doc)
    # tokens = map(lambda x: nltk.word_tokenize(x), nltk.sent_tokenize(text))
    # print(tokens)

    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    # print(entities)

def event_pairs_to_file():
    timeml_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
    corpus = corpus_checker.get_corpus_filenames(timeml_dir)
    with open('all_tlinks.txt', 'w') as writefile:
        for corpus_file in corpus:
            print('Working on {}...'.format(corpus_file))
            for event_pair in get_event_pairs(timeml_parser.get_document_root(timeml_dir + corpus_file)):
                writefile.write(str(event_pair) + '\n')
    print('done')
            

def get_event_pairs(doc):
    events = timeml_parser.get_events(doc)
    times = timeml_parser.get_timexs(doc)
    instances = timeml_parser.get_instances(doc)
    tlinks = timeml_parser.get_tlinks(doc)
    event_pairs = []
    for tlink in tlinks:
        try:
            a = [instance.get('eventID') for instance in instances if instance.get('eiid') == tlink['eventInstanceID']]
            if len(a) > 1:
                raise ValueError('Should only be one eventID')
            a = a[0]
            a = [''.join(event.itertext()).strip() for event in events if event.get('eid') == a]
            if len(a) > 1:
                raise ValueError('Should only be one event per eventID')
            a = a[0].lower()
        except KeyError:
            a = [time for time in times if time.get('tid') == tlink['timeID']]
            if len(a) > 1:
                raise ValueError('Should only be one timeID')
            a = a[0]
            t = a.get('type').lower()
            if t == 'date' or t == 'time':
                a = a.get('value')
            elif t == 'duration' or t == 'set':
                a = ''.join(a.itertext()).strip()
            else:
                print('\033[93m> {}\033[0m'.format(t))
            a = a.lower()
            # a = '#timex#'
        try:
            b = [instance.get('eventID') for instance in instances if instance.get('eiid') == tlink['relatedToEventInstance']]
            if len(b) > 1:
                raise ValueError('Should only be one eventID')
            b = b[0]
            b = [''.join(event.itertext()).strip() for event in events if event.get('eid') == b]
            if len(b) > 1:
                raise ValueError('Should only be one event per eventID')
            b = b[0].lower()
        except KeyError:
            b = [time for time in times if time.get('tid') == tlink['relatedToTime']]
            if len(b) > 1:
                raise ValueError('Should only be one timeID')
            b = b[0]
            t = b.get('type').lower()
            if t == 'date' or t == 'time':
                b = b.get('value')
            elif t == 'duration' or t == 'set':
                b = ''.join(b.itertext()).strip()
            else:
                print('\033[93m> {}\033[0m'.format(t))
            b = b.lower()
            # b = '#timex#'
        event_pairs.append((a, tlink['relType'], b))
    return event_pairs


import nltk

def count_event_pairs():
    with open('all_tlinks.txt', 'r') as readfile:
        fdist = nltk.FreqDist(readfile)
        with open('all_tlinks.freq.txt', 'w') as writefile:
            for f in fdist.most_common():
                writefile.write(str(f) + '\n')


if len(sys.argv) > 1:
    if sys.argv[1] == 'check':
        check_corpus(sys.argv[2:])
    elif sys.argv[1] == 'examine':
        examine_output()
    elif sys.argv[1] == 'nltk':
        other_stuff()
    elif sys.argv[1] == 'min':
        get_minimal_substrings(sys.argv[2])
    elif sys.argv[1] == 'text':
        try:
            output_text(sys.argv[2], sys.argv[3])
        except IndexError:
            output_text(sys.argv[2])
    elif sys.argv[1] == 'box':
        if sys.argv[2] == '--preserve':
            tml_to_box(sys.argv[3], True)
        else:
            tml_to_box(sys.argv[2])
    elif sys.argv[1] == 'bs':
        preserve = False
        if sys.argv[2] == '--preserve':
            preserve = True
            infile = sys.argv[3]
        else:
            infile = sys.argv[2]
        m = re.search(r'^(.*)\.tml$', infile)
        fname = m.group(1)
        tml_to_box(infile, preserve)
        print('Generating strings...')
        with open(fname + '.strings', 'w') as printfile:
            for tl in get_minimal_substrings(infile, False):
                printfile.write('* {}\n'.format(tl))
        print('Done. Saved to {}.strings'.format(fname))
    elif sys.argv[1] == 'pairs':
        event_pairs_to_file()
    elif sys.argv[1] == 'countpairs':
        count_event_pairs()
    else:
        print('No arg given')
