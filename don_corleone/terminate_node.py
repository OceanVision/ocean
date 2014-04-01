import os
import json
import threading
import time
import logging
import urllib2, urllib
import sys



MASTER = "master"
LOCAL = "local"
LOCAL_ADDRESS = "localhost:8881"
MASTER_LOCAL = "master_local"
MASTER_LOCAL_URL = "master_local_url"
RESPONSIBILITIES = "node_responsibilities"

def get_don_corleone_url(config):
    if(config[MASTER_LOCAL]): return config[MASTER_LOCAL_URL]
    else: return config[MASTER]



if __name__ == "__main__":
    config = json.load(open("config.json","r"))

    response = urllib2.urlopen(get_don_corleone_url(config)
                               +"/terminate_node?node_id="+config["node_id"]).read()

    print "Terminating node response ",response
