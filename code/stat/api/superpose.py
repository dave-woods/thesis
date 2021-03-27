from http.server import BaseHTTPRequestHandler
import apiscripts.wsf
import json


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        ll = json.loads(post_data)['data']
        result = dict()
        try:
            result['strings'] = list(apiscripts.wsf.superpose_all_langs_sensible(ll['strings'], ll['limit']))
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
