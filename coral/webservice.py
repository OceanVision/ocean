from flask import Flask
from flask import request, redirect, Response, url_for
import json
app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('about'))

@app.route('/about')
def about():
    return 'Coral Service for Ocean'

@app.route('/get_article_list', methods=['GET', 'POST'])
def get_article_list():
    request_data = request.get_json()
    last_news_id = request_data['last_news_id']
    count = request_data['count']
    feed_id = request_data['feed_id']

    # TODO: implementation

    response_data = []
    for i in range(0, count):
        response_data.append({
            'article_id': '974eeacc-87{0}a-11e3-9f3a-2cd05ae1c39b'.format(i % 10),
            'author': 'Autor {0}'.format(i),
            'title': 'Naglowek {0}'.format(i),
            'time': 1397664087,
            'description': 'Opis {0}'.format(i),
            'image_source': 'http://icons.iconarchive.com/icons/designcontest'
                            '/ecommerce-business/256/news-icon.png'
        })

    response_data = {'article_list': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

@app.route('/get_article_details', methods=['GET', 'POST'])
def get_article_details():
    request_data = request.get_json()
    article_id = request_data['article_id']

    # TODO: implementation

    response_data = []
    response_data.append({
        'article_id': '974eeacc-873a-11e3-9f3a-2cd05ae1c39b',
        'body': 'Tekst 7',
    })

    response_data = {'article_details': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

@app.route('/get_feed_list', methods=['GET', 'POST'])
def get_feed_list():
    request_data = request.get_json()
    user_id = request_data['user_id']

    # TODO: implementation

    response_data = []
    response_data.append({
        'link': 'http://www.tvn24.pl/',
        'title': 'TVN24.pl - Wiadomosci z kraju i ze swiata'
    })
    response_data.append({
        'link': 'http://www.gry-online.pl/',
        'title': 'GRY-OnLine'
    })

    response_data = {'feed_list': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

@app.route('/add_feed', methods=['POST'])
def add_feed():
    request_data = request.get_json()
    user_id = request_data['user_id']
    feed_tags = request_data['feed_tags']

    # TODO: implementation

    response_data = True

    response_data = {'status': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    request_data = request.get_json()
    username = request_data['username']
    password = request_data['password']

    # TODO: implementation

    response_data = '974eeacc-a07d-11e3-9f3a-2cd05ae1c39b'

    response_data = {'user_id': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    request_data = request.get_json()
    user_id = request_data['user_id']

    # TODO: implementation

    response_data = True

    response_data = {'status': response_data}
    response = Response(json.dumps(response_data), mimetype='application/json')
    return response

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=14)
