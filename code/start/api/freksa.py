from http.server import BaseHTTPRequestHandler
import json

# Allens
def equals(x, y):
    return ['|' + x + ',' + y + '|']
def before(x, y):
    return ['|' + x + '||' + y + '|']
def after(x, y):
    return before(y, x)
def meets(x, y):
    return ['|' + x + '|' + y + '|']
def meets_inv(x, y):
    return meets(y, x)
def starts(x, y):
    return ['|' + x + ',' + y + '|' + y + '|']
def starts_inv(x, y):
    return starts(y, x)
def finishes(x, y):
    return ['|' + y + '|' + x + ',' + y + '|']
def finishes_inv(x, y):
    return finishes(y, x)
def during(x, y):
    return ['|' + y + '|' + x + ',' + y + '|' + y + '|']
def during_inv(x, y):
    return during(y, x)
def overlaps(x, y):
    return ['|' + x + '|' + x + ',' + y + '|' + y + '|']
def overlaps_inv(x, y):
    return overlaps(y, x)

# Freksa
def older(x, y):
    return fi(x,y) + di(x,y) + m(x,y) + b(x,y) + o(x,y)
def younger(x, y):
    return older(y, x)
def head_to_head(x, y):
    return s(x, y) + si(x, y) + e(x, y)
def tail_to_tail(x, y):
    return f(x, y) + fi(x, y) + e(x, y)
def survived_by(x, y):
    return b(x, y) + m(x, y) + o(x, y) + s(x, y) + d(x, y)
def survives(x, y):
    return survived_by(y, x)
def precedes(x, y):
    return b(x, y) + m(x, y)
def succeeds(x, y):
    return precedes(y, x)
def contemporary(x, y):
    return o(x, y) + fi(x, y) + di(x, y) + si(x, y) + e(x, y) + s(x, y) + d(x, y) + f(x, y) + oi(x, y)
def born_before_death(x, y):
    return precedes(x, y) + contemporary(x, y)
def died_after_birth(x, y):
    return born_before_death(y, x)
def older_survived_by(x, y):
    return precedes(x, y) + o(x, y)
def younger_survives(x, y):
    return older_survived_by(y, x)
def older_contemporary(x, y):
    return o(x, y) + fi(x, y) + di(x, y)
def younger_contemporary(x, y):
    return older_contemporary(y, x)
def surviving_contemporary(x, y):
    return di(x, y) + si(x, y) + oi(x, y)
def survived_by_contemporary(x, y):
    return surviving_contemporary(y, x)
def unknown(x, y):
    return precedes(x, y) + contemporary(x, y) + succeeds(x, y)

# Mnemonics
def e(x, y):
    return equals(x, y)
def b(x, y):
    return before(x, y)
def bi(x, y):
    return after(x, y)
def m(x, y):
    return meets(x, y)
def mi(x, y):
    return meets_inv(x, y)
def s(x, y):
    return starts(x, y)
def si(x, y):
    return starts_inv(x, y)
def f(x, y):
    return finishes(x, y)
def fi(x, y):
    return finishes_inv(x, y)
def d(x, y):
    return during(x, y)
def di(x, y):
    return during_inv(x, y)
def o(x, y):
    return overlaps(x, y)
def oi(x, y):
    return overlaps_inv(x, y)

def un(x, y):
    return unknown(x, y)
def ol(x, y):
    return older(x, y)
def hh(x, y):
    return head_to_head(x, y)
def yo(x, y):
    return younger(x, y)
def sb(x, y):
    return survived_by(x, y)
def tt(x, y):
    return tail_to_tail(x, y)
def sv(x, y):
    return survives(x, y)
def pr(x, y):
    return precedes(x, y)
def bd(x, y):
    return born_before_death(x, y)
def ct(x, y):
    return contemporary(x, y)
def db(x, y):
    return died_after_birth(x, y)
def sd(x, y):
    return succeeds(x, y)
def ob(x, y):
    return older_survived_by(x, y)
def oc(x, y):
    return older_contemporary(x, y)
def sc(x, y):
    return surviving_contemporary(x, y)
def bc(x, y):
    return survived_by_contemporary(x, y)
def yc(x, y):
    return younger_contemporary(x, y)
def ys(x, y):
    return younger_survives(x, y)

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        passed_data = json.loads(post_data)['data']
        result = dict()
        try:
            result['strings'] = globals()[passed_data['rel']](passed_data['e1'], passed_data['e2'])
        except Exception as e:
            result['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        return
