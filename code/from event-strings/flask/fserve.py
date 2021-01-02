from flask import Flask, jsonify, request, render_template
from flask_redis import FlaskRedis

from sfg import superpose_all
    

app = Flask(__name__)
redis_store = FlaskRedis(app)
redis_key = "my_key" # won't work the way I want

@app.route('/hello', methods=['GET', 'POST'])
def hello():

    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        return 'OK', 200

    # GET request
    else:
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers

@app.route('/')
def index_page():
    x = superpose_all(['|a||b|', '|c|b,c|c|'])
    try:
        y = next(x)
    except StopIteration:
        y = 'Finished'
    # look inside `templates` and serve `index.html`
    return render_template('index.html', string=y)

@app.route('/other', methods=['GET', 'POST'])
def other_page():
    # look inside `templates` and serve `other.html`
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        json = request.get_json()
        sp = superpose_all(json['strings'])
        return render_template('other.html',string1=next(sp))
    return render_template('other.html')

if __name__ == "__main__":
    app.run(debug=True)