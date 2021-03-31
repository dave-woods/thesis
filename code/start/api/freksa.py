from http.server import BaseHTTPRequestHandler
import apiscripts.freksa
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        passed_data = json.loads(post_data)['data']
        result = dict()
        try:
            result['strings'] = getattr(apiscripts.freksa, passed_data['rel'])(passed_data['e1'], passed_data['e2'])
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
