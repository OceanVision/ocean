import json
import urllib2, urllib
import logging
import os
import sys
from don_corleone_constants import *



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

def get_all_services(config=None):
    if config is None:
        config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))
    
    resp = json.loads(run_procedure(config, "get_services"))
    if not has_succeded(resp):
        return None

    return resp['result']        


def get_service(services, service_id=None, service_name=None, node_id=None, service_params={}):
    for s in services:
        if service_id is not None and s[SERVICE_ID] != service_id:
            continue
        if service_name is not None and s[SERVICE] != service_name:
            continue
        if node_id is not None and s[NODE_ID] != node_id:
            continue

        config_cpy = dict(s[SERVICE_PARAMETERS])
        config_cpy.update(service_params)
 
        if set(config_cpy) != set(s[SERVICE_PARAMETERS]):
            continue

        return s

    return None

def get_running_service(service_id=None, node_id=None, service_name=None, service_params={}, \
                        node_config=None, enforce_running=True, enforce_local=False):
    """ 
        @returns given service if service is running with given optionally service_id
        or service_name and having parameters specified in params 

        @note Also if don corleone is not running it pulls config from config.json
        and assumes running_services==node_responsibilities
    """
    if service_id is None and service_name is None and len(service_params) == 0:
        logger.error("Incorrect parameters")
        return None

    if node_config is None:
        node_config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))
    
    if (node_config[MASTER_LOCAL] and os.system("./scripts/don_corleone_test.sh") != 0) or enforce_local:
        logger.error(os.system("./scripts/don_corleone_test.sh"))
        logger.error("WARNING: don corleone is not running !! Pulling config from config.json")
        services = []
        for node_resp in node_config["node_responsibilities"]:
            services.append({"local":True, SERVICE:node_resp[0], SERVICE_ID:node_resp[0], SERVICE_PARAMETERS:node_resp[1], NODE_ID:node_id})
        return get_service(services, service_id = service_id, node_id=node_id,  service_name=service_name, service_params=service_params)

    # Get running services from don corleone
    
    response = json.loads(run_procedure(node_config, "get_services"))

    if not has_succeded(response):
        logger.error("FAILED DON CORLEONE COMMUNICATION")
        return None

    services = []

    if enforce_running:
        services = [s for s in json.loads(run_procedure(node_config, "get_services"))['result'] if s[SERVICE_STATUS] == STATUS_RUNNING]
    else:    
        services = [s for s in json.loads(run_procedure(node_config, "get_services"))['result']]
    
    return get_service(services, service_id = service_id, node_id=node_id, service_name=service_name, service_params=service_params)

    

def has_succeded(response): 
    return 'result' in response




def get_configuration_query(param_name, node_id=None, service_id=None, service_name=None, service_params={}, config=None):
    """ 
        More complicated version of get_configuration 

        First checks for services registered in Don Corleone and
        if that fails checks for services defined in config.json

        Also if don corleone is not running it pulls config from config.json
    """
    

    s = get_running_service(service_id=service_id, node_id=node_id,  service_name=service_name, \
        service_params=service_params, node_config=config, enforce_running=False)

    # Try local
    if s is None:
        s = get_running_service(service_id=service_id, node_id=node_id, service_name=service_name, \
            service_params=service_params, node_config=config, enforce_running=False,\
            enforce_local=True
            ) 

    if s is None: 
        logger.error("Not found requested service!")
        return None


    # Special handling for config.json
    if s.get("local", False) is True:
        logger.error("WARNING: don corleone is not running !! Pulling config from config.json")
        if param_name in s[SERVICE_PARAMETERS]:
            return s[SERVICE_PARAMETERS][param_name]
        else:
            raise "Not found configuration. Try adding it to don_corleone/config.json" 
   
    # Handles request back to server
    return _get_configuration_by_id(s[SERVICE_ID], param_name, config)


def get_my_config():
    return json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))

def get_my_node_id():
    config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))
    return config['node_id']


def get_configuration(service_name, config_name, config=None, service_params={}):
    """
        @returns configuration config_name for service_name. 

        First checks for services registered in Don Corleone and
        if that fails checks for services defined in config.json

        Also if don corleone is not running it pulls config from config.json
    """

    s = get_running_service(service_id=None, service_name=service_name, \
        service_params=service_params, node_config=config, enforce_running=False)



    # Try local 
    if s is None:
        logger.info("No given service registered on don corleone!")
        s = get_running_service(service_id=None, service_name=service_name, \
            service_params=service_params, node_config=config, enforce_running=False,\
            enforce_local=True
            )

    if s is None: 
        logger.error("Not found requested service!")
        return None


    # Special handling for config.json
    if s.get("local", False) is True:
        if config_name in s[SERVICE_PARAMETERS]:
            return s[SERVICE_PARAMETERS][config_name]
        else:
            raise "Not found configuration. Try adding it to don_corleone/config.json" 


    # Handles request back to server
    return _get_configuration_by_id(s[SERVICE_ID], config_name, config)
   
   

def _get_configuration_by_id(service_id, config_name, config=None):

    if config is None:
        config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))


    if config[MASTER_LOCAL] and os.system("./scripts/don_corleone_test.sh") != 0:
        raise "Error - not running don - should nt call _get_configuration_by_id"
 
    try:
        params = urllib.urlencode({"service_id":service_id, "node_id":config[NODE_ID], "config_name":config_name})
        response = json.loads(urllib2.urlopen(get_don_corleone_url(config)+"/get_configuration?%s" % params).read())

       # Sometimes it is incompatible
        if has_succeded(response):
            if response['result'] is str or response['result'] is unicode:
                response['result'] = response['result'].replace("http","")
                response['result'] = response['result'].replace("127.0.0.1", "localhost")
            return response['result']

        logger.error("Failed don corleone get_config with don error "+response['error'])
        return None

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logger.error("Failed get_configuration with error "+str(e))
        return None


OCEAN_ROOT_MARKER_FILE = '.__ocean_root__'


def get_ocean_root_dir():
    """
        Search for the root directory location and return it
    """
    # TODO: Store it inside don_corleone config.json? It is inside ;) "home" ;p
    lookup_dir = './'
    while not os.path.isfile(lookup_dir + OCEAN_ROOT_MARKER_FILE):
        lookup_dir += '../'
        if os.path.abspath(lookup_dir) == '/':
            raise SystemError(
                'Ocean root directory could not be found. '
                'Is there a ' + OCEAN_ROOT_MARKER_FILE + ' file inside it?'
            )
    return os.path.abspath(lookup_dir)