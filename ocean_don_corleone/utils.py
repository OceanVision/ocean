import json
import urllib2, urllib
import logging
import os
import sys

#TODO: move to another class
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),"server.log"), )
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch_file.setFormatter(formatter)
logger.addHandler(ch_file)

MASTER = "master"
def get_configuration(name):
    config = json.load(open("config.json","r"))
    params = urllib.urlencode({"name":name})
    response = json.loads(urllib2.urlopen(config[MASTER]+"/get_configuration?%s" % params).read())

    # Sometimes it is incompatible
    if isinstance(response, str) or isinstance(response, unicode):
        response = response.replace("http://127.0.0.1", "localhost")

    print name, response

    # Check if error
    if isinstance(response, str) or isinstance(response, unicode) and response[0:5] == "error": #ya, pretty lame;)
        raise response

    return response