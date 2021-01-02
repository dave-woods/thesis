import timeml_parser
import corpus_checker
from functools import reduce
import matplotlib.pyplot as plt

def get_relation_counts (relations):
    """
    Convert a list of a document's relations to a dict with counts of the TimeML relations.

    Arguments:
    relations -- A list containing all of the TimeML relations found in a document's TLINKs.

    Return:
    A dictionary whose keys are the TimeML relation names, and whose values are the counts of those relations in the document.
    """
    return {
                'BEFORE': relations.count('BEFORE'),
                'AFTER': relations.count('AFTER'),
                'IS_INCLUDED': relations.count('IS_INCLUDED'),
                'INCLUDES': relations.count('INCLUDES'),
                'DURING': relations.count('DURING'),
                'DURING_INV': relations.count('DURING_INV'),
                'IBEFORE': relations.count('IBEFORE'),
                'IAFTER': relations.count('IAFTER'),
                'BEGINS': relations.count('BEGINS'),
                'BEGUN_BY': relations.count('BEGUN_BY'),
                'ENDS': relations.count('ENDS'),
                'ENDED_BY': relations.count('ENDED_BY'),
                'SIMULTANEOUS': relations.count('SIMULTANEOUS'),
                'IDENTITY': relations.count('IDENTITY')
            }

def document_difference (d1, d2):
    """
    A score for how different two documents are in terms of their temporal relation make up.
    
    Arguments:
    d1 -- the first document
    d2 -- the second document

    Return:
    A percentage value for the difference between the documents.
    """
    result = 0
    for key in d1:
        result = result + abs(d1[key] - d2[key])
    return round(result / 2, 4)

def sum_document_counts (d1, d2):
    """
    A function for summing up documents' relation counts.

    Arguments:
    d1 -- the first document
    d2 -- the second document

    Return:
    A dictionary which is the sum of the two inputs.
    """
    result = {}
    for key in d1:
        result[key] = d1[key] + d2[key]
    return result

def get_relation_percentages (relations):
    """
    Arguments:
    relations -- A dictionary (representing a document) whose keys are relation names, and whose values are the counts of those relations within that document.

    Return:
    A dictionary whose keys are relation names, and whose values are the relative percentages of each relation.
    """
    total = sum(relations.values())
    result = {}
    for k in relations:
        result[k] = round(relations[k] / total * 100, 2)
    return result

def get_mean_counts (documents):
    """
    Arguments:
    documents -- A list of dictionaries (representing documents) whose keys are relation names, and whose values are the counts of those relations in that document.

    Return:
    A dictionary whose keys are relation names, and whose values are the mean counts for the corpus.
    """
    corpus_length = len(documents)
    result = reduce(sum_document_counts, documents)
    for k in result:
        result[k] = result[k] / corpus_length
    return result

def timeml_to_allen_relations (document, include_inverses=False):
    """
    Convert from TimeML relations to more standard Allen Relations.

    Arguments:
    document -- A dictionary (representing a document) whose keys are TimeML relation names, and whose values are the counts of those relations in that document.
    include_inverses -- A boolean indicating whether to collapse inverses (e.g. before and after) into a single relation.

    Return:
    A dictionary whose keys are Allen Relation names, and whose values are the counts of those relations in the document.
    """
    if include_inverses:
        return {
                'before': document['BEFORE'] + document['AFTER'],
                'during': document['DURING'] + document['DURING_INV'] + document['INCLUDES'] + document['IS_INCLUDED'],
                'meets': document['IBEFORE'] + document['IAFTER'],
                'starts': document['BEGINS'] + document['BEGUN_BY'],
                'finishes': document['ENDS'] + document['ENDED_BY'],
                'equals': document['SIMULTANEOUS'] + document['IDENTITY']
                }
    else:
        return {
                'before': document['BEFORE'],
                'after': document['AFTER'],
                'during': document['DURING'] + document['IS_INCLUDED'],
                'during_inv': document['DURING_INV'] + document['INCLUDES'],
                'meets': document['IBEFORE'],
                'meets_inv': document['IAFTER'],
                'starts': document['BEGINS'],
                'starts_inv': document['BEGUN_BY'],
                'finishes': document['ENDS'],
                'finishes_inv': document['ENDED_BY'],
                'equals': document['SIMULTANEOUS'] + document['IDENTITY']
                }

# Get corpus data into useable form
corpus_dir = '/home/david/pgrad/TimeBank/corpus/timebank_1_2/data/timeml/'
filenames = corpus_checker.get_corpus_filenames(corpus_dir)
fileroots = list(map(lambda x: timeml_parser.get_document_root(corpus_dir + x), filenames))

# Total number of documents
# int
corpus_size = len(fileroots)

# List of TLinks from every document
# list(list({relType: str, eventInstanceID: str, relatedToEventInstance: str, timeID: str, relatedToTime: str}))
all_tlinks = list(map(lambda x: timeml_parser.get_tlinks(x), fileroots))

# Just the relation types for each document
# list(list(str))
all_reltypes = list(map(lambda x: list(
    map(lambda y: y['relType'], x)
    ), all_tlinks))

# The set of interval names for each document
# list(list(str))
all_intervals = list(map(lambda x: list(
    set(
        [item for sublist in list(
            map(
                lambda y: [
                    y.get('eventInstanceID'),
                    y.get('relatedToEventInstance'),
                    y.get('timeID'),
                    y.get('relatedToTime')
                    ],
                x)
            )
            for item in sublist if item is not None]
        )
    ), all_tlinks))

# The number of unique intervals in each document
# list(int)
intervals_per_document = list(map(lambda x: len(x), all_intervals))

# The total number of unique intervals in the corpus
# int
total_intervals = sum(intervals_per_document)

# The counts of each relation type for each document
# list({'BEFORE': int, 'AFTER': int, ...})
all_relation_counts = list(map(get_relation_counts, all_reltypes))

# The number of relations in each document
# list(int)
relations_per_document = list(map(lambda x: sum(x.values()), all_relation_counts))

# The total number of each relation type in the document
# {'BEFORE': int, 'AFTER': int, ...}
total_relation_counts = reduce(sum_document_counts, all_relation_counts)

# The total number of relations in the corpus
# int
total_relations = sum(total_relation_counts.values())

# The relative percentage for each relation type per document
# list({'BEFORE': float, 'AFTER': float, ...})
all_relation_percentages = list(map(get_relation_percentages, all_relation_counts))

# The mean relative percentage for each relation type for the whole corpus
# {'BEFORE': float, 'AFTER': float, ...}
mean_relation_percentages = get_relation_percentages(get_mean_counts(all_relation_counts))

# A zipped combination of each document's total intervals and relations
# list(tuple(int, int), tuple(int, int), ...)
intervals_vs_relations_per_document = list(zip(intervals_per_document, relations_per_document))

# An unzipped copy of the above that is sorted by number of intervals
# list(tuple(int, int, ...), tuple(int, int, ...))
intervals_vs_relations_per_document_sorted = list(zip(*sorted(intervals_vs_relations_per_document, key=lambda x: x[0])))

# Percentage values based on Allen Relation names rather than TimeML names
# list({'before': float, 'meets': float, ...})
allen_percentages = list(map(lambda x: get_relation_percentages(timeml_to_allen_relations(x, True)), all_relation_counts))

# Convert list of dicts to dict of lists (for graphing purposes)
# {'BEFORE': list(int), 'AFTER': list(int), ...}
arc = { k: [d[k] for d in all_relation_counts] for k in all_relation_counts[0] }
# {'BEFORE': list(float), 'AFTER': list(float), ...}
arp = { k: [d[k] for d in all_relation_percentages] for k in all_relation_percentages[0] }
# {'before': list(float), 'meets': list(float), ...}
alp = { k: [d[k] for d in allen_percentages] for k in allen_percentages[0] }

# The ratio between the number of relations per document to the number of intervals per document
# list(float)
relation_to_interval_ratios = [x[1] / x[0] for x in intervals_vs_relations_per_document]

# Normalising the above
rmin = min(relation_to_interval_ratios)
rmax = max(relation_to_interval_ratios)
normalised_relation_to_interval_ratios = relation_to_interval_ratios
for i, r in enumerate(relation_to_interval_ratios):
    normalised_relation_to_interval_ratios[i] = (relation_to_interval_ratios[i] - rmin) / (rmax - rmin)

arpf = list(zip(all_relation_percentages, filenames, relations_per_document))
all_document_differences = []

for idx, (p1, f1, r1) in enumerate(arpf):
    for p2, f2, r2 in arpf[idx+1:]:
        if f1 != f2:
            dd = document_difference(p1, p2)
            all_document_differences.append((f1, r1, f2, r2, r1/r2, dd))

all_document_differences = sorted(all_document_differences, key=lambda a: a[5])
for add in (all_document_differences[0:5]):
    print(add)
print('.\n.\n.')
for add in (all_document_differences[-11:-1]):
    print(add)








#  hist_range = (0, 1)
#  hist_bins = 20
#  plt.hist(normalised_relation_to_interval_ratios, hist_bins, hist_range)
#  plt.xlabel('normalised relations per interval')
#  plt.ylabel('frequency')
#  plt.title('Relations per interval ratio (normalised)')
#  plt.savefig('graphs/relations_per_interval_histogram_normalised.png')
#  plt.show()


#  plt.scatter(intervals_per_document, normalised_relation_to_interval_ratios, s=2)
#  plt.xlabel('intervals')
#  plt.ylabel('normalised(relations/intervals)')
#  plt.title('Ratio of relations to intervals (normalised)')
#  plt.savefig('graphs/ratio_relations_per_interval_normalised.png')
#  plt.show()


#  plt.scatter(ipd, arc['BEFORE'], s=2)
#  plt.xlabel('intervals')
#  plt.ylabel('BEFORE counts')
#  plt.title('BEFORE counts vs intervals')
#  #  plt.savefig('BEFORE_count_vs_intervals.png')
#  plt.show()

#  for rel in allen_percentages:
    #  plt.scatter(ipd, allen_percentages[rel], s=2)
    #  plt.xlabel('intervals')
    #  plt.ylabel('{} percentages'.format(rel))
    #  plt.title('{} percentages vs intervals'.format(rel))
    #  plt.savefig('graphs/flattened/flattened_{}_percentage_vs_intervals.png'.format(rel))
    #  plt.show()


# Verify that: ceiling(num-ints / 2) <= num-rels <= choose(num-ints, 2)
#  import math
#  print([x for x in intervals_vs_relations_per_document if x[1] < math.ceil(x[0] / 2) or x[1] > (x[0] * (x[0] - 1) * 0.5)])




#  with open('timebank-tlink-normalised.txt', 'w') as printfile:
    #  #  printfile.write('i-count : BEFORE,AFTER,IS_INCLUDED,INCLUDES,DURING,DURING_INV,IBEFORE,IAFTER,BEGINS,BEGUN_BY,ENDS,ENDED_BY,SIMULTANEOUS,IDENTITY\n')
    #  printfile.write('intervs : BEFOR, AFTER, IS_IN, INCLU, DURIN, DUR_I, IBEFO, IAFTE, BEGIN, BGNBY, ENDS , ENDBY, SIMUL, IDENT\n')
    #  for i, f in enumerate(all_relation_percentages):
        #  f = {k: v / intervals_per_document[i] for k, v in f.items()}
        #  printfile.write(' {:4d}   : {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}\n'.format(intervals_per_document[i], f['BEFORE'], f['AFTER'], f['IS_INCLUDED'], f['INCLUDES'], f['DURING'], f['DURING_INV'], f['IBEFORE'], f['IAFTER'], f['BEGINS'], f['BEGUN_BY'], f['ENDS'], f['ENDED_BY'], f['SIMULTANEOUS'], f['IDENTITY']))

    #  printfile.write('\nTotals:\n\n')
    #  f = total_percentages
    #  f = {k: v / total_intervals for k, v in f.items()}
    #  printfile.write(' {:4d}   : {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}\n'.format(total_intervals, f['BEFORE'], f['AFTER'], f['IS_INCLUDED'], f['INCLUDES'], f['DURING'], f['DURING_INV'], f['IBEFORE'], f['IAFTER'], f['BEGINS'], f['BEGUN_BY'], f['ENDS'], f['ENDED_BY'], f['SIMULTANEOUS'], f['IDENTITY']))

    #  printfile.write('\nAverages:\n\n')
    #  f = mean_relation_percentages
    #  f = {k: v / (total_intervals / len(intervals_per_document)) for k, v in f.items()}
    #  printfile.write('{:5.2f}   : {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}, {:5.2f}\n'.format(round(total_intervals / len(intervals_per_document), 2), f['BEFORE'], f['AFTER'], f['IS_INCLUDED'], f['INCLUDES'], f['DURING'], f['DURING_INV'], f['IBEFORE'], f['IAFTER'], f['BEGINS'], f['BEGUN_BY'], f['ENDS'], f['ENDED_BY'], f['SIMULTANEOUS'], f['IDENTITY']))
    #  printfile.close()


