""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.
"""


modules = []
"""
Each module is represented as a dictionary with fields:

* ip/domain
* pid
* status

"""


### Flask module ###

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello world!"

@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    name = request.args.get('name')
    return "Hello world!"

@app.route('/get_status', methods=['GET']):
def get_status:
    pass

app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    app.run(port=8881)