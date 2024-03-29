from http.server import BaseHTTPRequestHandler
import apiscripts.strfns
import json

def string_to_rel(string, x):
    t, m = apiscripts.strfns.analogous_strings(string, '|X||Y|')
    if t:
        return 'BEFORE' if m[x] == 'X' else 'AFTER'
    t, m = apiscripts.strfns.analogous_strings(string, '|X|Y|')
    if t:
        return 'IBEFORE' if m[x] == 'X' else 'IAFTER'
    t, m = apiscripts.strfns.analogous_strings(string, '|X,Y|')
    if t:
        return 'SIMULTANEOUS'
    t, m = apiscripts.strfns.analogous_strings(string, '|X|X,Y|X|')
    if t:
        return 'INCLUDES' if m[x] == 'X' else 'DURING'
    t, m = apiscripts.strfns.analogous_strings(string, '|X|X,Y|')
    if t:
        return 'ENDED_BY' if m[x] == 'X' else 'ENDS'
    t, m = apiscripts.strfns.analogous_strings(string, '|X,Y|X|')
    if t:
        return 'BEGUN_BY' if m[x] == 'X' else 'BEGINS'
    t, m = apiscripts.strfns.analogous_strings(string, '|X|X,Y|Y|')
    if t:
        return 'OVERLAPS' if m[x] == 'X' else 'OVERLAPPED_BY'
    return 'UNKNOWN'

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        passed_data = json.loads(post_data)['data']
        result = dict()
        try:
            vocab = passed_data['vocabulary']
            strings = None
            try:
                strings = frozenset(apiscripts.strfns.flatten_list(apiscripts.strfns.superpose_all_langs_sensible(passed_data['strings'], 12)))
            except:
                strings = frozenset(apiscripts.strfns.flatten_list(passed_data['strings']))
            idx = 0
            lid = 0
            links = []
            for v in vocab:
                for w in vocab[idx+1:]:
                    p = apiscripts.strfns.projection_lang_full_vocab(strings, [v, w])
                    if len(p) > 0:
                        r = '|'.join(map(lambda s: string_to_rel(s, v), p))
                        links.append('<TLINK lid="{0}" {1}="{2}" {3}="{4}" relType="{5}" />'.format(lid, 'eventID' if v[0] == 'e' else 'timeID', v, 'relatedToEvent' if w[0] == 'e' else 'relatedToTime', w, r))
                        lid += 1
                idx += 1
            result['tlinks'] = links
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
