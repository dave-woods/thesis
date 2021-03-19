from browser import document, html, window, bind
import sys

# '__main__' because freksa is the first loaded
# second would be '__main__2'
freksa = sys.modules['__main__']

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
    except IndexError:
        window.alert('Not enough events to form a relation!')
    except KeyError:
        window.alert('Can\'t relate event to itself!')
    except ValueError:
        window.alert('Contradiction found in event relations!')

@bind(document['lz'], 'change')
def register_tlink(ev):
    [first,rel,second] = document['lz'].value.split(',')
    rel_strings = getattr(freksa, rel)(first, second)
    window.addSuperpositionResults([rel_strings])
