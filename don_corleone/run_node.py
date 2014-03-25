"""
Simple script for running node given node configuration
"""
from optparse import OptionParser

def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option(
        "-c",
        "--config",
        dest="config",
        type="str",
        default="config.json",
        help="File with configuration for running node"
    )
    return parser


import os
import json
import threading
import time
import logging
import urllib2, urllib
from signal import *
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


MASTER = "master"
MASTER_LOCAL = "master_local"
NODE_ID = "node_id"
RESPONSIBILITIES = "node_responsibilities"


#Does run_node own don_corleone
run_node_owner = False
terminated = False

from utils import get_don_corleone_url
def install_node(config, run=False):
    global terminated
    """ Waits for webserver to start """

    while os.system("./scripts/don_corleone_test.sh") != 0 and not terminated:
        time.sleep(1)

    if terminated:
        exit(0)

    time.sleep(3)
    logger.info("Installing the node")
    print config[RESPONSIBILITIES]

    if not run:
        logger.info("WARNING: Only installing not running services")


    for id, responsibility in enumerate(config[RESPONSIBILITIES]):
        logger.info("Registering "+str(id)+" responsibility "+str(responsibility))



        service = responsibility[0]

        additional_config = responsibility[1]


        params = urllib.urlencode\
                ({"service":json.dumps(service),"run":json.dumps(run) , "config":json.dumps(config),
                  "additional_config":json.dumps(additional_config), "node_id":json.dumps(config[NODE_ID])
                  })


        response = urllib2.urlopen(get_don_corleone_url(config)+"/register_service", params).read()



        print response

        response = urllib2.urlopen(get_don_corleone_url(config)+"/get_services").read()

        print json.loads(response)['result']

config = []

def clean(*args):
    global terminated

    try:
        logger.info("Terminating node by terminating node in DonCorleone and terminating DonCorleone if local")
        ret = os.system("python terminate_node.py")

        if ret != 0:
            logger.error("Failed terminating node")
        else:
            logger.info("Terminated node successfully")

        if run_node_owner:
            ret = os.system("./scripts/don_corleone_terminate.sh")
            if ret != 0:
                logger.error("Failed terminating don corleone")
                logger.error("Return code = "+str(ret))
            else:
                logger.info("Terminated Ocean DonCorleone successfully")

    except Exception, e:
        pass
    finally:
        terminated=True


if __name__ == "__main__":
    # Read in parameters
    parser = create_parser()
    (opt, args) = parser.parse_args()

    #Load configuration files
    config = json.load(open(opt.config,"r"))

    logger.info(("Configuration file ", config))


    #Check if run_node should create Don Corleone
    if config.get(MASTER_LOCAL, False):
        logger.info("Checking if run_node should run the don_corleone service")
        if os.system("./scripts/don_corleone_test.sh") != 0:
            logger.info("Running DonCorleone on master setting")
            run_node_owner = True
            os.system("./scripts/run.sh don ./scripts/don_corleone_run.sh")


    #Clean shutdown
    for sig in (SIGINT,):
        signal(sig, clean)

    #Install
    install_node(config)    
