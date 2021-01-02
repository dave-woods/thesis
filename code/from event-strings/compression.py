import string_functions_old
import timeml_parser
import corpus_checker
import settings

settings.init(log_level='ALL')

corpus_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
filenames = corpus_checker.get_corpus_filenames(corpus_dir)
fileroots = list(map(lambda x: timeml_parser.get_document_root(corpus_dir + x), filenames))

all_tlinks = list(map(lambda x: timeml_parser.get_tlinks(x), fileroots))

def compression_map (tlink):
    rType = 'x,y'
    if tlink['relType'] in ['BEFORE', 'IBEFORE']:
        rType = 'x|y'
    elif tlink['relType'] in ['AFTER', 'IAFTER']:
        rType = 'y|x'
    else:
        rType = 'x,y'
    #  rType = '|x,y|'
    #  if tlink['relType'] in ['BEFORE', 'IBEFORE']:
        #  rType = '|x|y|'
    #  elif tlink['relType'] in ['AFTER', 'IAFTER']:
        #  rType = '|y|x|'
    #  else:
        #  rType = '|x,y|'
    x = tlink.get('timeID', tlink.get('eventInstanceID'))
    y = tlink.get('relatedToTime', tlink.get('relatedToEventInstance'))
    return rType.replace('x', x).replace('y', y)

for doc, name in zip(all_tlinks, filenames):
    new_doc = list(map(lambda tl: compression_map(tl), doc))
    strings = corpus_checker.string_sorter(new_doc)
    strings = corpus_checker.run_pw_superposition(strings)
    strings = list(filter(lambda x: x != '-', strings))
    strings = list(map(lambda x: x if len(x) > 1 else x[0], strings))
    if settings.is_issue_found():
        print(name, ': # : problems found')
        settings.log_issues()
        settings.clear_issues()
    else:
        print(name, ':', len(strings), ':', strings)
    print()
