from flask import Flask
from flask import redirect, url_for
app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('about'))

@app.route('/about')
def about():
    return 'Coral Service for Ocean'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=14)
