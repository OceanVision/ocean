import urllib2, urllib
import json


MASTER = "master"
MASTER_LOCAL = "master_local"
NODE_ID = "node_id"
RESPONSIBILITIES = "node_responsibilities"

def count_services(config):
    response = urllib2.urlopen(config[MASTER] +"/get_services").read()
    return len(json.loads(response)['result'])
