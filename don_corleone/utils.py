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
NODE_ID = "node_id"
MASTER_LOCAL = "master_local"
MASTER_LOCAL_URL = "master_local_url"

def get_don_corleone_url(config):
    if(config[MASTER_LOCAL]): return config[MASTER_LOCAL_URL]
    else: return config[MASTER]

def get_configuration(service_name, config_name):
    config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))
    params = urllib.urlencode({"service_name":service_name, "node_id":config[NODE_ID], "config_name":config_name})
    response = json.loads(urllib2.urlopen(get_don_corleone_url(config)+"/get_configuration?%s" % params).read())['result']

    # Sometimes it is incompatible
    if isinstance(response, str) or isinstance(response, unicode):
        response = response.replace("http://127.0.0.1", "localhost")

    print service_name, response

    # Check if error
    if isinstance(response, str) or isinstance(response, unicode) and response[0:5] == "error": #ya, pretty lame;)
        raise response

    return response
