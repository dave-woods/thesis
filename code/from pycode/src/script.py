from browser import document, html, window, bind, worker
import freksa
from win_string_functions import superpose_all_langs_sensible

event_strings = []

@bind(document['createRelation'], 'click')
def create_relation(ev):
    try:
        first = [option.value for option in document.select('.ev1')[0] if option.selected][0]
        second = [option.value for option in document.select('.ev2')[0] if option.selected][0]
        if first == second:
            raise KeyError
        rel = [option.value for option in document.select('.rel')[0] if option.selected][0]
        rel_strings = getattr(freksa, rel)(first, second)
        window.addSuperpositionResults([rel_strings])
        # window.updateStrings(rel_strings, ['|'+first+'|', '|'+second+'|'])
        # event_strings = window.getStrings() + [rel_strings]

        # if len(event_strings) > 1:
        #     # print(event_strings)
        #     sp = superpose_all_langs_sensible(event_strings, 31)
        #     # sp0 = next(sp)
        #     # if len(sp) == 0:
        #     #     event_strings = window.getStrings()
        #     #     raise ValueError
        #     # else:
        #     print(next(sp))
        #     print(next(sp))
                # pass
                # window.updateStrings([],[], sp)
    except IndexError:
        window.alert('Not enough events to form a relation!')
    except KeyError:
        window.alert('Can\'t relate event to itself!')
    except ValueError:
        window.alert('Contradiction found in event relations!')

my_worker = worker.Worker('myworker')

@bind(document['dosp'], 'click')
def do_super(ev):
    current = window.getStrings()
    my_worker.send(current)

@bind(my_worker, "message")
def onmessage(e):
    print(e.data)
    # window.addSuperpositionResults(list(sp))

    # sp = superpose_all_langs_sensible(current, 13)
    # window.addSuperpositionResults(list(sp))

@bind(document['lz'], 'change')
def register_tlink(ev):
    [first,rel,second] = document['lz'].value.split(',')
    rel_strings = getattr(freksa, rel)(first, second)
    window.addSuperpositionResults([rel_strings])

