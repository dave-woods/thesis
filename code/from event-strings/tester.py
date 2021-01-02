# from string_functions import *
from corpus_checker import get_corpus_filenames
import timeml_parser as tml
from nltk.featstruct import FeatStruct
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()

def lemma_from_eiid(eiid, froot):
    events_by_eid = { e.get('eid'): e for e in tml.get_events(froot) }
    instances_by_eiid = { i.get('eiid'): i for i in tml.get_instances(froot) }
    instance = instances_by_eiid[eiid]
    try:
        return wnl.lemmatize(events_by_eid[instance.get('eventID')].text.lower(), pos=instance.get('pos')[0].lower())
    except KeyError:
        return wnl.lemmatize(events_by_eid[instance.get('eventID')].text.lower(), pos='n')

def lemma_from_tid(tid, froot):
    timexs_by_tid = { t.get('tid'): t for t in tml.get_timexs(froot) }
    return wnl.lemmatize(timexs_by_tid[tid].text.lower(), pos='n')

corpus = '/home/david/pgrad/TimeBank/latest/'
filename = 'ABC19980108.1830.0711.tml'
froot = tml.get_document_root(corpus+filename)
tlinks = tml.get_tlinks(froot)
inst_ids = dict()
time_ids = dict()
for link in tlinks:
    k = link.get('eventInstanceID')
    if k:
        try:
            inst_ids[k] = inst_ids[k]+1
        except KeyError:
            inst_ids[k] = 1
    k = link.get('relatedToEventInstance')
    if k:
        try:
            inst_ids[k] = inst_ids[k]+1
        except KeyError:
            inst_ids[k] = 1
    k = link.get('timeID')
    if k:
        try:
            time_ids[k] = time_ids[k]+1
        except KeyError:
            time_ids[k] = 1
    k = link.get('relatedToTime')
    if k:
        try:
            time_ids[k] = time_ids[k]+1
        except KeyError:
            time_ids[k] = 1
iii = list(inst_ids.items())
iii.sort(reverse=True,key=lambda l: l[1])
print(len(iii))
print(iii[:10])
tii = list(time_ids.items())
tii.sort(reverse=True,key=lambda l: l[1])
print(len(tii))
print(tii[:10])
allii = iii#+tii
allii.sort(reverse=True,key=lambda l: l[1])
lemii = []
for ii in allii:
    lemii.append((lemma_from_eiid(ii[0], froot) if ii[0].startswith('ei') else lemma_from_tid(ii[0], froot), ii[1]))
print(len(allii))
# print(allii[:10])
print(lemii[:10])










######################################

# filename = '/home/david/pgrad/TimeBank/latest/ABC19980108.1830.0711.tml'
# # filename = '/home/david/pgrad/TimeBank/latest/APW19980227.0468.tml'
# root = tml.get_document_root(filename)
# tlinks = tml.get_tlinks(root)
# ts = [s for s in tml.tlinks_to_strings(tlinks)]
# # print(ts)
# # print()
# # sp = superpose_all_langs_pick_shortest(ts[:3])
# # while True:
# #     print(next(sp))
# #     input('next')
# sp = superpose_all(ts)
# for s in sp:
#     print(s)
#     input('next')


# fs = tml.get_instance_featstructs(root)+tml.get_timex_featstructs(root)
# strings = tml.strings_to_fs_strings(ts, fs)
# tml.print_fs_string(strings[0])

########################################
########################################

# corpus = '/home/david/pgrad/TimeBank/latest/'
# filenames = get_corpus_filenames(corpus)

# # tot = 0
# # for f in filenames:
# #     r = tml.get_document_root(corpus+f)
# #     tot += len(tml.get_tlinks(r)) + len(tml.get_slinks(r))
# # print('links:', tot)
# # print('docs:', len(filenames))

# withstems = []
# withoutstems = []
# time0 = []
# time1 = []
# time2 = []
# docs_with_stems = set()
# for f in filenames:
#     froot = tml.get_document_root(corpus+f)
#     events = tml.get_events(froot)
#     events = {e.get('eid'): e for e in events}
#     instances = tml.get_instances(froot)
#     instances = {i.get('eiid'): i.get('eventID') for i in instances}
#     links = tml.get_tlinks(froot) + tml.get_slinks(froot)
#     for link in links:
#         ids = [link.get('eventInstanceID'), link.get('relatedToEventInstance')]
#         if ids[0] and ids[1]:
#             try:
#                 w = [FeatStruct({**{k: events.get(instances.get(i)).attrib[k] for k in ['class', 'stem']}, **{'text': events.get(instances.get(i)).text}}) for i in ids]
#                 withstems.append(w)
#                 docs_with_stems.add(f)
#             except KeyError:
#                 withoutstems.append([FeatStruct({**events.get(instances.get(i)).attrib, **{'text': events.get(instances.get(i)).text}}) for i in ids])
#         elif ids[0] and not ids[1]:
#             time0.append(ids[0])
#         elif not ids[0] and ids[1]:
#             time1.append(ids[1])
#         elif not ids[0] and not ids[1]:
#             time2.append('both')
# # print(len(withstems), len(docs_with_stems))
# # print(len(withoutstems))
# # print(len(time0))
# # print(len(time1))
# # print(len(time2))
# # print(withstems)
# # print(withoutstems)
# juststems = list(map(lambda p: [p[0].get('stem'),p[1].get('stem')], withstems))
# jsdict = dict()
# for js in juststems:
#     k = '-'.join(js)
#     try:
#         jsdict[k] = jsdict[k]+1
#     except KeyError:
#         jsdict[k] = 1
# jsi = list(jsdict.items())
# jsi.sort(reverse=True,key=lambda l: l[1])
# # print(len(jsi))
# # print(jsi[:10])

# justtext = list(map(lambda p: [p[0].get('text'),p[1].get('text')], withoutstems+withstems))
# jtdict = dict()
# for jt in justtext:
#     k = '-'.join(jt)
#     try:
#         jtdict[k] = jtdict[k]+1
#     except KeyError:
#         jtdict[k] = 1
# jti = list(jtdict.items())
# jti.sort(reverse=True,key=lambda l: l[1])
# # print(len(jti))
# # print(jti[:10])

# fjti = [p for p in jti if p[0].split('-')[0] != p[0].split('-')[1]]
# # print(len(fjti))
# # print(fjti[:10])

# ffjti = [p for p in fjti if p[0].split('-')[0] not in ['said', 'says'] and p[0].split('-')[1] not in ['said', 'says']]
# # print(len(ffjti))
# # print(ffjti[:10])

# # singles_multis = [len([p for p in jti if p[1] == 1]), len([p for p in jti if p[1] > 1])]
# # print('[singles, multis]:', singles_multis)


# justclasses = list(map(lambda p: [p[0].get('class'),p[1].get('class')], withoutstems+withstems))
# jcdict = dict()
# for jc in justclasses:
#     k = '-'.join(jc)
#     try:
#         jcdict[k] = jcdict[k]+1
#     except KeyError:
#         jcdict[k] = 1
# jci = list(jcdict.items())
# jci.sort(reverse=True,key=lambda l: l[1])
# # print(len(jci))
# # print(jci[:10])

# with open('outputs/jci.txt', 'w') as wfile:
#     wfile.write(str(len(jci)) + '\n')
#     for j in jci:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')


#######################

# corpus = '/home/david/pgrad/TimeBank/latest/'
# filenames = get_corpus_filenames(corpus)
# csdict = dict()
# ctdict = dict()
# for f in filenames:
#     froot = tml.get_document_root(corpus+f)
#     events = tml.get_events(froot)
#     for event in events:
#         try:
#             cs = '-'.join([event.get('stem'), event.get('class')])
#             try:
#                 csdict[cs] = csdict[cs]+1
#             except KeyError:
#                 csdict[cs] = 1
#         except TypeError:
#             pass
#         ct = '-'.join([event.text, event.get('class')])
#         try:
#             ctdict[ct] = ctdict[ct]+1
#         except KeyError:
#             ctdict[ct] = 1
# csi = list(csdict.items())
# csi.sort(reverse=True,key=lambda l: l[1])
# cti = list(ctdict.items())
# cti.sort(reverse=True,key=lambda l: l[1])
# print(len(csi))
# print(csi[:10])

# with open('outputs/csi.txt', 'w') as wfile:
#     wfile.write(str(len(csi)) + '\n')
#     for j in csi:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')

# print(len(cti))
# print(cti[:10])

# with open('outputs/cti.txt', 'w') as wfile:
#     wfile.write(str(len(cti)) + '\n')
#     for j in cti:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')

#######################################

# corpus = '/home/david/pgrad/TimeBank/latest/'
# filenames = get_corpus_filenames(corpus)
# lemcla = dict()
# for f in filenames:
#     froot = tml.get_document_root(corpus+f)
#     events = tml.get_events(froot)
#     instances = tml.get_instances(froot)
#     i_by_eid = { i.get('eventID') : i for i in instances }
#     for event in events:
#         pos = i_by_eid[event.get('eid')].get('pos')
#         try:
#             lem = wnl.lemmatize(event.text.lower(), pos=pos[0].lower())
#         except KeyError:
#             lem = wnl.lemmatize(event.text.lower(), pos='n')
#         lc = '-'.join([lem, event.get('class')])
#         try:
#             lemcla[lc] = lemcla[lc]+1
#         except KeyError:
#             lemcla[lc] = 1

# lci = list(lemcla.items())
# lci.sort(reverse=True,key=lambda l: l[1])
# print(len(lci))
# print(lci[:10])

# with open('outputs/lci.txt', 'w') as wfile:
#     wfile.write(str(len(lci)) + '\n')
#     for j in lci:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')

# lci.sort(key=lambda l: l[0])
# with open('outputs/lci_alpha.txt', 'w') as wfile:
#     wfile.write(str(len(lci)) + '\n')
#     for j in lci:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')

##############################

# corpus = '/home/david/pgrad/TimeBank/latest/'
# filenames = get_corpus_filenames(corpus)

# freqs = dict()
# for f in filenames:
#     froot = tml.get_document_root(corpus+f)
#     events = tml.get_events(froot)
#     events_by_eid = { e.get('eid'): e for e in events }
#     instances = tml.get_instances(froot)
#     instances_by_eiid = { i.get('eiid'): i for i in instances }
#     tlinks = tml.get_tlinks(froot)
#     for link in tlinks:
#         eiids = [link.get('eventInstanceID'), link.get('relatedToEventInstance')]
#         if eiids[0] and eiids[1]:
#             ins = [instances_by_eiid[eiid] for eiid in eiids]
#             evs = [events_by_eid[i.get('eventID')] for i in ins]
#             poss = [i.get('pos')[0].lower() for i in ins]
#             lems = ['', '']
#             for idx in [0, 1]:
#                 try:
#                     lems[idx] = wnl.lemmatize(evs[idx].text.lower(), pos=poss[idx])
#                 except KeyError:
#                     lems[idx] = wnl.lemmatize(evs[idx].text.lower(), pos='n')
#             k = '-'.join([lems[0], evs[0].get('class'), lems[1], evs[1].get('class'), link.get('relType')])
#             try:
#                 freqs[k] = freqs[k]+1
#             except KeyError:
#                 freqs[k] = 1
# fri = list(freqs.items())
# fri.sort(reverse=True,key=lambda l: l[1])
# print(len(fri))
# print(fri[:10])

# with open('outputs/fri.txt', 'w') as wfile:
#     wfile.write(str(len(fri)) + '\n')
#     for j in fri:
#         wfile.write(j[0] + ',' + str(j[1]) + '\n')