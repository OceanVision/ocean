import urllib2, urllib
import json
import os

MASTER = "master"
MASTER_LOCAL = "master_local"
NODE_ID = "node_id"
RESPONSIBILITIES = "node_responsibilities"
PUBLIC_URL = "public_ssh_domain"
MASTER = "master"
MASTER_LOCAL = "master_local"
MASTER_LOCAL_URL = "master_local_url"
NODE_ID = "node_id"
RESPONSIBILITIES = "node_responsibilities"
REVERSED_SSH = "ssh-reversed"
SSH_HOST = "public_ssh_domain"
SSH_PORT = "ssh-port"
SSH_USER = "ssh-user"



def get_test_config(config_name):
    """ Replaces necessary fields to assure cross-machine testing """


    config_node = json.load(open(os.path.join(os.path.dirname(__file__),"../config.json"),"r"))


    # Prepare config file
    config_test = json.load(open(os.path.join(os.path.dirname(__file__),config_name),"r"))
    config_test["home"] = config_node["home"]
    config_test[SSH_HOST] = config_node[SSH_HOST]
    config_test[SSH_PORT] = config_node[SSH_PORT]
    config_test[SSH_USER] = config_node[SSH_USER]
 
    return config_test


def count_services(config, running=False):
    response = urllib2.urlopen(config[MASTER_LOCAL_URL] +"/get_services?running="+("true" if running else "false")).read()
    return len(json.loads(response)['result'])
