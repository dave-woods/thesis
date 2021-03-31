import settings

def get_document_root(filename):
    import xml.etree.ElementTree as ET
    return ET.parse(filename).getroot()

def get_text(doc_root):
    return ''.join(doc_root.itertext()).strip()

def get_tlinks(doc_root):
    return [inst for inst in doc_root.iter('TLINK')]
def get_slinks(doc_root):
    return [inst for inst in doc_root.iter('SLINK')]
def get_instances(doc_root):
    return [inst for inst in doc_root.iter('MAKEINSTANCE')]
def get_events(doc_root):
    return [inst for inst in doc_root.iter('EVENT')]
def get_timexs(doc_root):
    return [inst for inst in doc_root.iter('TIMEX3')]

def tlink_to_string(tlink_el):
    tlink = tlink_el.attrib
    try:
        a, a_type = tlink['eventInstanceID'], 'eventInstanceID'
    except KeyError:
        a, a_type = tlink['timeID'], 'timeID'
    try:
        b, b_type = tlink['relatedToEventInstance'], 'relatedToEventInstance'
    except KeyError:
        b, b_type = tlink['relatedToTime'], 'relatedToTime'
    if a == b:
        if tlink['relType'] != 'SIMULTANEOUS' and tlink['relType'] != 'IDENTITY':
            settings.issue_found(3,'SELF_REFERENT')
        if settings.__log_level >= settings.__LOG_LEVELS['WARN_INFO']:
            print('\033[93m' + 'WARNING: An event should not be related to itself.\n{0} and {1} given with relType {2}'.format(a, b, tlink['relType']) + '\033[0m')
        if settings.__strict_self_referent_mode:
            raise Exception
    try:
        raw_string = {
            'BEFORE': '|{0}||{1}|',
            'AFTER': '|{1}||{0}|',
            'INCLUDES': '|{0}|{0},{1}|{0}|',
            'DURING_INV': '|{0}|{0},{1}|{0}|',
            'IS_INCLUDED': '|{1}|{1},{0}|{1}|',
            'DURING': '|{1}|{1},{0}|{1}|',
            'SIMULTANEOUS': '|{0},{1}|',
            'IDENTITY': '|{0},{1}|',
            'IBEFORE': '|{0}|{1}|',
            'IAFTER': '|{1}|{0}|',
            'BEGINS': '|{0},{1}|{1}|',
            'BEGUN_BY': '|{1},{0}|{0}|',
            'ENDS': '|{1}|{0},{1}|',
            'ENDED_BY': '|{0}|{1},{0}|',
        }[tlink['relType']]
        return raw_string.format(a, b)
    except KeyError:
        settings.issue_found(3, 'UNKNOWN_RELATION')
        if settings.__log_level >= settings.__LOG_LEVELS['ALL']:
            print('\033[91m' + 'ERROR: Unknown relation type encountered.\nrelType: {0}\n{1}: {2}\n{3}: {4}\n'.format(tlink['relType'], a_type, a, b_type, b) + '\033[0m')
        raise

def tlinks_to_strings(tlinks):
    return [tlink_to_string(t) for t in tlinks]

from nltk.featstruct import FeatStruct
def get_instance_featstructs(root):
    instances = get_instances(root)
    events = get_events(root)
    for i in instances:
        try:
            i.set('event', next(FeatStruct({**{k: e.attrib[k] for k in ['class', 'stem']}, **{'text': e.text}}) for e in events if e.get('eid') == i.get('eventID')))
        except KeyError:
            i.set('event', next(FeatStruct({**{k: e.attrib[k] for k in ['class']}, **{'text': e.text}}) for e in events if e.get('eid') == i.get('eventID')))
    return [FeatStruct({k: i.attrib[k] for k in set(i.keys()) - set(['eventID'])}) for i in instances]

def get_timex_featstructs(root):
    timexs = get_timexs(root)
    return [FeatStruct(t.attrib) for t in timexs]

def get_fs_strings(root):
    tl = get_tlinks(root)
    ifs = get_instance_featstructs(root)
    tfs = get_timex_featstructs(root)
    fs = ifs+tfs
    tlstrs = tlinks_to_strings(tl)
    return strings_to_fs_strings(tlstrs, fs)

def strings_to_fs_strings(strs, fs):
    fsstrs = []
    for t in strs:
        a = [c.split(',') for c in t.split('|')]
        am = [[next(f for f in fs if (fl == f.get('eiid') or fl == f.get('tid'))) for fl in c if fl != ''] for c in a]
        fsstrs.append(am)
    return fsstrs

def print_fs_string(fs_string):
    for box in fs_string[:-1]:
        if len(box) == 0:
            print('[]\n----------------------------------------')
        else:
            print('[')
            for fs in box[:-1]:
                print(fs,end='\n,\n')
            print(box[-1])
            print(']\n----------------------------------------')
    box = fs_string[-1]

    if len(box) == 0:
        print('[]')
    else:
        print('[')
        for fs in box[:-1]:
            print(fs,end='\n,\n')
        print(box[-1])
        print(']')
    print()
