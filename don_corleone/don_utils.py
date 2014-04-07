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

def run_procedure(config, name):
    response = urllib2.urlopen(get_don_corleone_url(config)
                               +"/"+name).read()
    return response



def has_succeded(response): 
    return 'result' in response

def get_configuration(service_name, config_name, config=None):
    """
        Returns configuration config_name for service_name. 

        For compatibility if in config value is http it is replaced with ""
        and if there is 127.0.0.1 it is replaced with localhost

    """
    if config is None:
        config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))

    try:
        params = urllib.urlencode({"service_name":service_name, "node_id":config[NODE_ID], "config_name":config_name})
        response = json.loads(urllib2.urlopen(get_don_corleone_url(config)+"/get_configuration?%s" % params).read())['result']

       # Sometimes it is incompatible
        if has_succeded(response):
            response = response.replace("http","")
            response = response.replace("127.0.0.1", "localhost")
            return response
        else:
            raise response['error']

    except:
        for node in config["node_responsibilities"]:
            if node[0] == service_name:
                if config_name in node[1]:
                    return node[1][config_name]
                else:
                    raise "Not found configuration. Try adding it to don_corleone/config.json" 

 
