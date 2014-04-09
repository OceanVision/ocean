"""
Simple script for running node given node configuration
"""
import os
import json
import threading
import time
import logging
import urllib2, urllib
from signal import *
import sys



from terminate_node import terminate_node
from optparse import OptionParser
from don_corleone_client import run_client, logger
config = []


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

def run_node(config, hang=True):
    """ Run node
        @param config Loaded json configuration
        @param hang is true while true at the end (register signal if used 
            in code)
    """

    state_callback = {'value':False}

    if not hang:
        import threading
        t = threading.Thread(target=run_client, args=(config, state_callback))
        t.daemon = True
        t.start()

        # Wait for installation finish
        while state_callback['value'] is False:
            time.sleep(0.1)

    else:
        run_client(config, state_callback)


def clean(*args):
    try:
        logger.info("Terminating node by terminating node in DonCorleone and terminating DonCorleone if local")
        ret = terminate_node(config)
        print "Termianted?"

        if ret is False:
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
        exit(0)



if __name__ == "__main__":
    #Clean shutdown
    for sig in (SIGINT,):
        signal(sig, clean) 


    # Read in parameters
    parser = create_parser()
    (opt, args) = parser.parse_args()

    #Load configuration files
    config = json.load(open(opt.config,"r"))

    logger.info(("Configuration file ", config))

    run_node(config, hang=True)

