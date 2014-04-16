from flask import Flask
from flask import request, redirect, make_response, url_for
import json
app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('about'))

@app.route('/about')
def about():
    return 'Coral Service for Ocean'

@app.route('/get_news_list', methods=['POST'])
def get_news_list():
    request_data = request.get_json()
    last_news_id = request_data['last_news_id']
    count = request_data['count']
    feed_id = request_data['feed_id']

    response_data = []
    for i in range(0, count):
        response_data.append({
            'author': 'Autor {0}'.format(i),
            'title': 'Naglowek {0}'.format(i),
            'body': 'Tekst {0}'.format(i),
            'image_source': 'http://icons.iconarchive.com/icons/designcontest'
                            '/ecommerce-business/256/news-icon.png'
        })

    return make_response(json.dumps(response_data))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=14)
