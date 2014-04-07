import os
import json
import threading
import time
import logging
import urllib2, urllib
import sys

from don_utils import get_don_corleone_url, has_succeded


MASTER = "master"
LOCAL = "local"
LOCAL_ADDRESS = "localhost:8881"
MASTER_LOCAL = "master_local"
MASTER_LOCAL_URL = "master_local_url"
RESPONSIBILITIES = "node_responsibilities"


def terminate_node(config):
    response = urllib2.urlopen(get_don_corleone_url(config)
                               +"/terminate_node?node_id="+config["node_id"]).read()
    print "Terminating node response ",response
    return has_succeded(response)


if __name__ == "__main__":
    config = json.load(open("config.json","r"))
    terminate_node(config)

