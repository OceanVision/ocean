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

RESPONSIBILITIES = "node_responsibilities"



if __name__ == "__main__":
    config = json.load(open("config.json","r"))

    response = urllib2.urlopen((config[MASTER] if config[MASTER] != LOCAL else LOCAL_ADDRESS)
                               +"/terminate_node").read()

    print "Terminating node response ",response