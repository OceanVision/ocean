"""
Implementation of don corleone client (using file locks)
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
from don_utils import get_don_corleone_url, has_succeded, don_test_file

from optparse import OptionParser
import time
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




logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


USER = "ssh-user"
PUBLIC_URL = "public_ssh_domain"
MASTER = "master"
MASTER_LOCAL = "master_local"
NODE_ID = "node_id"
RESPONSIBILITIES = "node_responsibilities"
REVERSED_SSH = "ssh-reversed"
SSH_HOST = "public_ssh_domain"
SSH_PORT = "ssh-port"


#Does run_node own don_corleone
run_node_owner = False
terminated = False

def install_node(node_config, run=True):
    global terminated
    """ Waits for webserver to start """

    while node_config[MASTER_LOCAL] and os.system(don_test_file) != 0 and not terminated:
        logger.info("Still don corleone not running. Try running it yourself using ./scripts/don_corleone_run.sh")
        time.sleep(1)

    if terminated:
        exit(0)

    # Terminating node
    logger.info("Terminating old responsibilities")
    response = urllib2.urlopen(get_don_corleone_url(node_config)+"/terminate_node?node_id="+node_config[NODE_ID]).read()
    print response

   
    logger.info("Registering the node")
    # Register node
    params = urllib.urlencode({"node_config":json.dumps(node_config), "node_id":json.dumps(node_config[NODE_ID]) })
    response = urllib2.urlopen(get_don_corleone_url(node_config)+"/register_node", params).read()
    logger.info(response)


    # Reversed ssh support
    if node_config.get(REVERSED_SSH, False):
        logger.info("Reversed ssh")
        response = json.loads(urllib2.urlopen(get_don_corleone_url(node_config)+"/register_reversed?node_id="+str(node_config[NODE_ID])).read())
        print response
        cmd = "./scripts/run_reversed_ssh.sh {0} {1} {2} {3} {4}".format(response["result"]["ssh-user"], response["result"]["ssh-host"], \
        response["result"]["ssh-port-redirect"], node_config[SSH_PORT], response['result']['ssh-port'])
        logger.info("Running "+cmd)
        os.system(cmd)


    time.sleep(1)
 
    logger.info("Installing the node")
    print node_config[RESPONSIBILITIES]

    if not run:
        logger.info("WARNING: Only installing not running services")


    service_ids = []
    for id, responsibility in enumerate(node_config[RESPONSIBILITIES]):
        logger.info("Registering "+str(id)+" responsibility "+str(responsibility))
        service = responsibility[0]
        service_parameters = responsibility[1]
        params = urllib.urlencode\
                ({"service":json.dumps(service),"run":json.dumps(False) , "node_config":json.dumps(node_config),
                  "additional_config":json.dumps(service_parameters), "node_id":json.dumps(node_config[NODE_ID]),
                  "public_url":json.dumps(node_config[PUBLIC_URL])
                  })


        print get_don_corleone_url(node_config)
        print "Registering and waiting for response..."
        response = urllib2.urlopen(get_don_corleone_url(node_config)+"/register_service", params).read()
        print "Response...", response

	if has_succeded(response):
	    service_ids.append(json.loads(response)['result'])
	else:
	    logger.error("NOT REGISTERED SERVICE "+str(responsibility))

        response = json.loads(urllib2.urlopen(get_don_corleone_url(node_config)+"/get_services").read())

        print "Succeded = ", has_succeded(response)

    if run:
        trails = 2000
        for service_id in service_ids:
            print "Running ",service_id
            for i in xrange(trails):
                print "Calling run service"
                response = urllib2.urlopen(get_don_corleone_url(node_config)+\
            "/run_service?service_id="+str(service_id)).read()
                print "Response..."
                if not has_succeded(response):
                    logger.error("SHOULDNT HAPPEN FAILED RUNNING "+service_id)
                    logger.error(response)
                else:
                    logger.info(response)
                    break

                time.sleep(1.0)

                if i == 4:
                    logger.error("Failed running service 20 times in a row. Abandoning")

#    for id, responsibility in enumerate(config[RESPONSIBILITIES]):


def timeout_command(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
      time.sleep(0.1)
      now = datetime.datetime.now()
      if (now - start).seconds> timeout:
        os.kill(process.pid, signal.SIGKILL)
        os.waitpid(-1, os.WNOHANG)
        return None
    return process.stdout.read()

def run_client(config, state_callback):
    """ Run node hanging !
        @param config Loaded json configuration
    """
    
    os.system("rm command_queue && rm command_queue_lock")

    # All commands will fail 

    #Check if run_node should create Don Corleone
    if config.get(MASTER_LOCAL, False):
        logger.info("Checking if run_node should run the don_corleone service")
        if os.system("./scripts/don_corleone_test.sh") != 0:
            logger.info("Running DonCorleone on master setting")
            run_node_owner = True
            os.system("./scripts/run.sh don ./scripts/don_corleone_run.sh")

    #Ensure command_queue exists
    os.system("rm command_queue")

    def install_node_daemon():
        #Install
        install_node(config)

        # Indicate having finished installing
        state_callback['value']=True


    t = threading.Thread(target=install_node_daemon)
    t.daemon = True
    t.start()





    #Run daemon - ONLY PROTOTYPED
    while True:
        while os.path.exists("command_queue_lock"):
            print "Locked.."
            time.sleep(0.01)

        os.system("sudo -u {0} touch command_queue_lock".format(config[USER]))

        commands = []

        if os.path.exists("command_queue"):
            commands = open("command_queue","r").readlines()
            os.system("sudo rm command_queue")


        os.system("sudo rm command_queue_lock".format(config[USER]))

        for cmd in commands:
            logger.info("Running remotedly requested command " + str(cmd))
            ret = os.system("sudo -E -u {0} sh -c \"{1}\"".format(config["ssh-user"], cmd))
            if ret != 0:
                logger.info("Failed command")
            logger.info("Done")

        time.sleep(1)

if __name__ == "__main__":
    # Read in parameters
    parser = create_parser()
    (opt, args) = parser.parse_args()

    #Load configuration files
    config = json.load(open(opt.config,"r"))

    logger.info(("Configuration file ", config))

    run_client(config)
