from http.server import BaseHTTPRequestHandler
import apiscripts.freksa
import apiscripts.wsf
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        ll = json.loads(post_data)['data']
        kb = ll['strings']
        result = dict()
        try:
            test_strings = getattr(apiscripts.freksa, ll['rel'])(ll['e1'], ll['e2'])
            result['strings'] = test_strings
            result['status'] = 'contradicted'
            if not any(any(apiscripts.wsf.lang_contradicts_string(lang, ts) for lang in kb) for ts in test_strings):
                result['status'] = 'possible'
                if any(any(apiscripts.wsf.lang_contains_string(lang, ts) for lang in kb) for ts in test_strings):
                    result['status'] = 'found'
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
