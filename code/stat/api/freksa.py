from http.server import BaseHTTPRequestHandler
import apiscripts.freksa
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        ll = json.loads(post_data)['data']
        result = dict()
        try:
            result['strings'] = getattr(apiscripts.freksa, ll['rel'])(ll['e1'], ll['e2'])
        except Exception as e:
            result['error'] = e

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
