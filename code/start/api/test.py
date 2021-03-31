from http.server import BaseHTTPRequestHandler
import apiscripts.freksa
import apiscripts.strfns
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        passed_data = json.loads(post_data)['data']
        kb = passed_data['strings']
        result = dict()
        try:
            test_strings = getattr(apiscripts.freksa, passed_data['rel'])(passed_data['e1'], passed_data['e2'])
            result['strings'] = test_strings
            result['status'] = 'contradicted'
            if not any(any(apiscripts.strfns.lang_contradicts_string(lang, ts) for lang in kb) for ts in test_strings):
                result['status'] = 'possible'
                if any(any(apiscripts.strfns.lang_contains_string(lang, ts) for lang in kb) for ts in test_strings):
                    result['status'] = 'found'
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
