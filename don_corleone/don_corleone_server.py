"""
# Server responsible for managing Ocean state.


    State: prototype: everything is based on dictionaries. I should add classes to parse everything. It is very error prone

    Note: it is not checking and asserting everything partially because of the design, partly because of the limited time resources ;)

    TODO: repalce literals in request.form accessors

    Ocean admin should be run on every node of our Ocean cluster.


## Key concepts

    configuration: node, or service config is a entity deifning its installtion, properties

    params: can change from run to run, defines service parameters like host/port

    arguments: these are arguments **pased** during running to the service, in most cases are derived from params


## Protocol:

    JSONP:
    if succeeded:
        {
            result: JSON(data)
        }
    if error:
         {
            error: JSON(data)
        }


Services are added and not tested for accessibility first time. Services are added
to service list which is periodically updated (terminated/running) status



Assumptions:
* SSH is non blocking (should timeout) NOTE: not timeouting right now
---------------
* Every command can fail - it is ok if terminate/run fails

"""
import json
import threading
import os
import subprocess
from don_corleone_constants import *
from don_utils import logger
from flask.ext.jsonpify import jsonify
from flask import g


#Configuration for services read from CONFIG_DIRECTORY
service_config = {}

#Nodes in the system
#Each node is "config" + "services"
registered_nodes = {}

#Services registered in the system
services = []

# Lock for synchronization
node_services_lock = threading.RLock()

# Sttatus of checker daemon
status_checker_job_status = "NotRunning"

# Default configs for services
default_service_params = {}


class DummySynchronizer:
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


class Synchronizer:
    def __enter__(self):
        global services, registered_nodes
        services = getattr(g, "_services", None)
        registered_nodes = getattr(g, "_registered_nodes", None)


    
    def __exit__(self, type, value, traceback):
        global services, registered_nodes
        json.dumps(services, )

synchronizer = DummySynchronizer()


import socket
import sys
import inspect

def pack_error(e):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    logger.error("error: "+str(calframe[1][3])+"::"+str(sys.exc_traceback.tb_lineno)+":"+str(e))
    return str(calframe[1][3])+"::"+str(sys.exc_traceback.tb_lineno)+":"+str(e)




def get_bare_ip(address):
    """ Return bare ip for address (ip->ip, domain -> ip) """
    address = str(address)
    try:
        return address if address[0].isdigit() else socket.gethostbyname(address)
    except Exception,e:
        logger.error("Error running get_bare_ip")
        logger.error(str(e))
        return address

def is_service_by_id(service_id):
    with synchronizer:
        return filter(lambda x: x[SERVICE_ID] == service_id, services)

#TODO: package as a class
def get_service_by_id(service_id):
    """ Returns service given service_id """
    if not filter(lambda x: x[SERVICE_ID] == service_id, services):
        raise ERROR_NOT_REGISTERED_SERVICE
    else:
        if len(filter(lambda x: x[SERVICE_ID] == service_id, services)) > 1:
            logger.error("Duplicated service_id")
            exit(1)

        result = filter(lambda x: x[SERVICE_ID] == service_id, services)[0]
    return result

def get_node_services(node_id):
    """ Returns service of given node_id"""
    with synchronizer:
        # Return is fine in with clause
        return [s for s in services if s[NODE_ID] == node_id]

#TODO: package as a class
def add_service(service):
    """ Adds service """
    with synchronizer:
        # Check if no duplicate or duplicate and local
        if not is_service_by_id(service[SERVICE_ID]) or service[SERVICE_LOCAL]:

            # Check if local then only one local
            if any([True for s in services if s[SERVICE] == service[SERVICE] and s[NODE_ID] == service[NODE_ID]]) and service[SERVICE] in UNARY_SERVICES:
                raise ERROR_DUPLICATE

            services.append(service)

            registered_nodes[service[NODE_ID]][NODE_RESPONSIBILITIES].append(service)
        else:
            logger.error("Error adding existing service_id")
            raise ERROR_DUPLICATE



#TODO: package as a class
def remove_service(service_id):
    """ Removes service from registered services """
    with synchronizer:
        found_id = None
        found_service = None
        #TODO: more functional style
        for id, service in enumerate(services):
            if service[SERVICE_ID] == service_id:
                found_id = id
                found_service = service

        #If doesn't exists it is ok
        if not found_service:
            return OK

        #Remove from services list
        services.pop(found_id)
        #Remove from registered node

        #Should be in registered_nodes. Remove from responsibilities
        if found_service[NODE_ID] not in registered_nodes:
            logger.error("Node not registered, fatal error")
            raise ERROR_NODE_NOT_REGISTERED
        else:
            with synchronizer:
                for id, m in enumerate(
                        registered_nodes[found_service[NODE_ID]][NODE_RESPONSIBILITIES]):
                    if m[SERVICE_ID] == service_id:
                        registered_nodes[found_service[NODE_ID]][NODE_RESPONSIBILITIES].pop(id)

        return OK


import time




#TODO: add throwing errors here
def cautious_run_cmd_over_ssh(cmd, node_id, m, sudo_queue=True):
    """ 
        Returns appropriate errors if encounters problems
        @note if sudo_queue is on it won't return proper errors :(
        @note Doesn't throw errors
    """

    
    n = registered_nodes[node_id]
    user, port, host = n[NODE_SSH_USER], n[NODE_SSH_PORT], n[NODE_SSH_HOST]


    # oStrictHostKeyChecking - sdisables asking for RSA key
    # note command_queue is only a prototype for communication between
    # daemon and script
    if sudo_queue:
        cmd = "ssh -oStrictHostKeyChecking=no {user}@{0} -p{1} -o ConnectTimeout=2 \"cd {3} && {4} '{2}'\"".\
                                format(host,\
                                        port,\
                                        cmd,\
                                        os.path.join(m[SERVICE_HOME], "don_corleone"),\
                                        "./scripts/enqueue_command.sh",\
                                        user=user\
                                    )
    else:
        cmd = "ssh -oStrictHostKeyChecking=no {user}@{0} -p{1} -o ConnectTimeout=2 \"{2}\"".\
                                format(host,\
                                        port,\
                                        cmd,\
                                        user=user
                                    )
 

    logger.info("Running ssh command: "+str(cmd))

    prog = subprocess.Popen([cmd
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = prog.communicate()

    logger.info(output)

    if prog.returncode != 0:
        logger.info("Error running command " + str(ERROR_FAILED_SSH_CMD)+ " "+str(prog.returncode))
        return (ERROR_FAILED_SSH_CMD, output)

    return (OK, output)

def update_status(m):
    """ Checks and updates status of given service  """
    logger.info("Updating status for " + str(m))





    cmd = "(cd {0} && {1})".format(
                                    os.path.join(m[SERVICE_HOME],"don_corleone"),
                                    "./scripts/{0}".format(service_config[m[SERVICE]][CONFIG_TEST_SCRIPT]))


    logger.info("Running {0} to check if service is running ".format(cmd))

    status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID], m, sudo_queue=False)



    with synchronizer:

        logger.info(("Checking server availability for ",m[SERVICE_ID], "result ", str(status)))
        logger.info(output)

        if status == ERROR_FAILED_SSH_CMD or status == ERROR_NOT_REACHABLE_SERVICE:
            logger.error("Service terminated")
            logger.error(output)
            m[SERVICE_STATUS] = STATUS_TERMINATED
            return

        m[SERVICE_STATUS] = STATUS_RUNNING

def status_checker_job():
    """ Check status of the jobs """
    logger.info("Running status checking daemon")
    while True:
        logger.info("Registered {0} services".format(len(services)))
        for m in services:
                update_status(m)

        with synchronizer:
            for n in registered_nodes.itervalues():
                ret = os.system("ping {0} -c 1".format(n[NODE_ADDRESS]))
                if ret != 0:
                    logger.info("Failed ping for "+NODE_ID)
                    n[NODE_LAST_PING_ANSWER] += 1
                else:
                    n[NODE_LAST_PING_ANSWER] = 0

                if n[NODE_LAST_PING_ANSWER] > KILL_NODE_COUNTER:
                      _terminate_node(n[NODE_ID])

        time.sleep(UPDATE_FREQ)


### Flask module ###

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)

#@app.before_first_request
def run_daemons():
    global status_checker_job_status
    status_checker_job_status = "Running"
    t = threading.Thread(target=status_checker_job)
    t.daemon = True
    t.start()



from don_utils import get_don_corleone_url

@app.route('/')
def hello():
    ### Render out url of server, very clever Staszek!
    return flask.render_template("index.html", server_url=get_don_corleone_url(json.loads(open("config.json","r").read())))

def _terminate_service(service_id):
    """ Terminate service given service_id
        @returns OK or DonCorleoneExcpetion
    """
    with synchronizer:
        if not get_service_by_id(service_id):
            raise ERROR_NOT_REGISTERED_SERVICE

        m = get_service_by_id(service_id)

        if m[SERVICE_STATUS] == STATUS_TERMINATED:
            return OK

        if m[SERVICE_STATUS] != STATUS_RUNNING:
            logger.error("Wrong service status")
            exit(1)


        cmd = "(cd {0} && {1})".format(
                                        os.path.join(m[SERVICE_HOME],"don_corleone"),
                                        "./scripts/run.sh terminating_job ./scripts/{0}".format(service_config[m[SERVICE]][CONFIG_TERMINATE_SCRIPT]))

    status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID],m)


    with synchronizer:
        logger.info(("Terminating service ",service_id, "output", output, "status ",status))

        if status == OK:
            m[SERVICE_STATUS] = STATUS_TERMINATED


        return status

def resolve_don_value(value, node_id):
    """
    @returns Resolved don value, for instance $node:host is service node's host (public_ssh_domain from config.json)
    """

    if str(value) == value:
        if len(value) == 0: return value

        if value[0] == "$" or value[0] == "%":
            s, config = value[1:].split(":")
            print s, config
            if s == "node":
                if config == "host":
                    with synchronizer:
                        return "localhost" if registered_nodes[node_id][NODE_ADDRESS] == "127.0.0.1" \
                            else registered_nodes[node_id][NODE_ADDRESS]
                else:
                    raise ERROR_NOT_RECOGNIZED_CONFIGURATION

            return _get_configuration(service_name=s, service_id=None, node_id=node_id, config_name=config)
        else:
            return value
    else:
        return value



def _run_service(service_id):
    try:
        """ Run service given service_id
            @returns OK or DonCorleone exception
        """
        with synchronizer:
            m = get_service_by_id(service_id)

            if m[SERVICE_STATUS] == STATUS_RUNNING:
                raise ERROR_SERVICE_ALREADY_RUNNING

            if m[SERVICE_STATUS] != STATUS_TERMINATED:
                logger.error("Wrong service status")
                exit(1)

            # Check dependencies
            for d in service_config[m[SERVICE]][CONFIG_DEPENDS]:
                try:
                    s = _get_service(d, None, m[NODE_ID])
                    if not s[SERVICE_STATUS] == STATUS_RUNNING:
                        raise ERROR_NOT_SATISFIED_DEPENDENCIES_NOT_RUNNING
                except Exception, e:
                    logger.error("Failed getting service in checking dependencies "+str(e))
                    raise e

            # Calculate params
            params = ""

            sign = " " if (m[SERVICE] == SERVICE_MANTIS_SHRIMP or m[SERVICE] == SERVICE_MANTIS_SHRIMP_MASTER) else "="

            for p in service_config[m[SERVICE]][CONFIG_ARGUMENTS]:
                if p[0] in m[SERVICE_PARAMETERS]:
                    params += " --{0}{2}{1}".format(p[0], m[SERVICE_PARAMETERS][p[0]], sign)
                else:
                    params += " --{0}{2}{1}".format(p[0], m[SERVICE_PARAMETERS].get(p[0], resolve_don_value(p[1], m[NODE_ID])), sign)





            logger.info("Running {0} with params ".format(m[SERVICE_ID], params))

            cmd = "(cd {0} && {1})".format(
                                            os.path.join(m[SERVICE_HOME],"don_corleone"),
                                            "./scripts/run.sh {1} ./scripts/{0} {2}".format(service_config[m[SERVICE]][CONFIG_RUN_SCRIPT], m[SERVICE_ID], params))

        status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID],m)

        with synchronizer:
            logger.info(("Running service ",service_id, "output", output, "status ",status))

        return status
    except Exception, e:
        raise DonCorleoneException(pack_error(e))

def _deregister_service(service_id):
    """ Deregister service given service_id
        @returns OK or DonCorleone exception
    """
    with synchronizer:

        #TODO: add special handling for local
        if not get_service_by_id(service_id):
            raise ERROR_NOT_REGISTERED_SERVICE

        if len(filter(lambda x: x[SERVICE_ID] == service_id, services)) > 1:
            logger.error("Duplicated service id")
            raise ERROR

#        logger.info("Terminating service")
#        _terminate_service(service_id)
        logger.info("Removing service")
        remove_service(service_id)

        return OK


@app.route('/deregister_service', methods=['GET'])
def deregister_service():

    service_id = request.args.get('service_id')
    try:
        output_run_service = _deregister_service(service_id)
        logger.info("Deregistering service "+service_id+" "+output_run_service)
        return jsonify(result=str(OK))
    except DonCorleoneException,e:
        logger.error("Failed deregistering service " + service_id + " with DonCorleoneException "+str(e))
        return jsonify(error=pack_error(e))
    except Exception,e:
        logger.error("Failed deregistering service " + service_id + " with unexpected error "+str(e))
        return jsonify(result=str(ERROR))

#q - ma wplyw : q-->0 : liczymy nie zerowe, q-->inf : rownomierne





from flask import Response
@app.route('/register_node', methods=['POST'])
def register_node():
    try:
        output = OK
        with synchronizer:
            node_config = json.loads(request.form['node_config'])
            node_id = json.loads(request.form['node_id'])

            with synchronizer:
                if not node_id in registered_nodes:
                    node = {NODE_ID:node_id, NODE_ADDRESS:node_config[CLIENT_CONFIG_SSH_HOST],NODE_CONFIG:node_config, NODE_RESPONSIBILITIES:[], NODE_SSH_HOST:node_config[CLIENT_CONFIG_SSH_HOST],
                    NODE_SSH_PORT:node_config[CLIENT_CONFIG_SSH_PORT], NODE_SSH_USER:node_config[CLIENT_CONFIG_SSH_USER]
                    }
                    registered_nodes[node_id] = node
            
            output=OK


        return jsonify(result=str(output))

    except Exception, e:
        logger.error((sys.exc_traceback.tb_lineno ))
        logger.error("Failed registering node with "+str(e))
        return jsonify(error=pack_error(e))


@app.route('/get_service', methods=['GET'])
def get_service():
    service_id = request.args.get('service_id')
    try:
        s = get_service_by_id(service_id)
        return jsonify(result=s)
    except Exception, e:
        return pack_error(e)


def _register_service(run, service_name, public_url, node_config, local, node_id, forced_service_params):
    try:

        with synchronizer:

            # Read in service and copy **parameters**
            service_params = dict(default_service_params[service_name])
            service_params.update(forced_service_params)
            for key in service_params.iterkeys():
                service_params[key] = resolve_don_value(service_params[key], node_id)


            service_id = None

            for node_resp in node_config[NODE_RESPONSIBILITIES]:
                if node_resp[0] == service_name:
                    service_id = node_resp[1].get('service_id', None)


            logger.info("Registering "+str(service_id)+ " service_name="+str(service_name) +" and run = "+str(run))

            with synchronizer:
                if not node_id in registered_nodes:
                    raise ERROR_NOT_REGISTERED_NODE

            # Check dependencies
            for d in service_config[service_name][CONFIG_DEPENDS]:
                try:
                    s = _get_service(d, None, node_id)
                except Exception, e:
                    raise ERROR_NOT_SATISFIED_DEPENDENCIES


            logger.info("Registering local="+str(local)+" service")


            #Prepare service id
            if service_id is None:
                services_id_test = 0
                service_list = [s[SERVICE_ID] for s in services if s[SERVICE] == service_name]
                logger.info("Testing "+service_name+"_"+str(services_id_test))
                while service_name+"_"+str(services_id_test) in service_list:
                    services_id_test += 1
                service_id = service_name + "_" + str(services_id_test)


            # Not known service..
            if service_name not in KNOWN_SERVICES:
                raise ERROR_NOT_RECOGNIZED_SERVICE

            if not service_name or not service_id or len(service_name)==0 or len(service_id)==0:
                raise ERROR_WRONG_METHOD_PARAMETERS

            # No duplicated service id
            if filter(lambda x: x[SERVICE_ID] == service_id, services):
                raise ERROR_SERVICE_ID_REGISTERED

            # Only one global service
            if filter(lambda x: x[SERVICE] == service_name and x[SERVICE_LOCAL]==False, services) and (service_name in UNARY_SERVICES) and (local is False):
                raise ERROR_ALREADY_REGISTERED_SERVICE

            logger.info("Proceeding to registering {0} {1}".format(service_name, service_id))


            #Prepare service
            service_dict = {
                       SERVICE:service_name,
                       SERVICE_ID:service_id,
                       SERVICE_STATUS:STATUS_TERMINATED,
                       NODE_ID: node_id,
                       NODE_ADDRESS: public_url,
                       SERVICE_LOCAL: local,
                       SERVICE_RUN_CMD:DEFAULT_COMMAND,
                       SERVICE_HOME:node_config[CLIENT_CONFIG_HOME],
                       SERVICE_PARAMETERS: service_params
            }


            #Modify service_id to make it unique


            add_service(service_dict)

            logger.info(("Registering " if not run else "Running and registering ")+str(service_dict))


            #update_status(service_dict)


            if run:
                logger.info("Running service "+service_id)
                service_id = service_dict[SERVICE_ID]
                try:
                    output_run_service = _run_service(service_dict[SERVICE_ID])
                    logger.info("Running service "+service_dict[SERVICE_ID]+" result "+output_run_service)
                except DonCorleoneException,e:
                    logger.error("Failed deregistering service " + service_id + " with DonCorleoneException "+str(e))
                    raise e
                except Exception,e:
                    logger.error("Failed deregistering service " + service_id + " with non expected exception "+str(e))
                    raise ERROR_FAILED_SERVICE_RUN

                if service_dict[SERVICE_STATUS] != STATUS_RUNNING:
                    raise ERROR_FAILED_SERVICE_RUN


            # Registers (without running!) "adds" services
            for service_to_add in service_config[service_name][CONFIG_ADDS]:
                logger.info("Adding child service "+str(service_to_add))
                service_to_add_name, service_to_add_params = service_to_add
                _register_service(False, service_to_add_name, public_url, node_config, local, node_id, service_to_add_params)

            return service_id
    except Exception ,e:
        raise DonCorleoneException(pack_error(e))

@app.route('/register_service', methods=['POST'])
def register_service():
    try:


        run = json.loads(request.form['run'])
        service_name = json.loads(request.form['service'])

        if service_name not in KNOWN_SERVICES:
            raise ERROR_NOT_RECOGNIZED_SERVICE

        public_url = json.loads(request.form['public_url'])
        node_config = json.loads(request.form['node_config'])

        node_id = json.loads(request.form['node_id'])
        # Load default service additional config (like port configuration)
        additional_service_parameters = {}
        if 'additional_config' in request.form:
            additional_service_parameters.update(json.loads(request.form['additional_config']))
        local = additional_service_parameters.get("local", False)


        service_id = \
            _register_service(run, service_name, public_url, node_config, local, node_id, additional_service_parameters)



        return jsonify(result=service_id)

    except Exception, e:
        return jsonify(error=pack_error(e))



@app.route('/terminate_service')
def terminate_service():
    service_id = request.args.get('service_id')

    # Try terminating the service and delegate errror checking to _run_service
    try:
        output_run_service = _terminate_service(service_id)

        logger.info("Terminating service "+service_id+" result "+output_run_service)
        return jsonify(result=str(OK))
    except DonCorleoneException,e:
        logger.error("Failed terminating service " + service_id + " with DonCorleoneException "+str(e))
        return jsonify(error=pack_error(e))
    except Exception,e:
        logger.error("Failed terminating service " + service_id + " with non expected exception "+str(e))
        return jsonify(error=str(ERROR_FAILED_SERVICE_RUN))








@app.route('/run_service')
def run_service():
    service_id = request.args.get('service_id')
    global services
    """ Check status of the jobs """

    # Try running the service and delegate errror checking to _run_service
    try:
        output_run_service = _run_service(service_id)
        logger.info("Running service "+str(service_id)+" result "+str(output_run_service))
        return jsonify(result=str(OK))
    except DonCorleoneException,e:
        logger.error("Failed running service " + service_id + " with DonCorleoneException "+str(e))
        return jsonify(error=pack_error(e))
    except Exception,e:
        logger.error("Failed running service " + service_id + " with non expected exception "+str(e))
        return jsonify(result=pack_error(e))



import flask

@app.route('/get_services')
def get_services():
    running = request.args.get('running')
    if running == "true":
        return jsonify(result=[s for s in services if s[SERVICE_STATUS] == STATUS_RUNNING])
    else:
        return jsonify(result=services)

@app.route('/get_nodes')
def get_nodes():
    return jsonify(result=registered_nodes)



def _get_service(service_name, service_id=None, node_id=None):
        # Check parameters
        if node_id is None:
            raise ERROR
        # Get appropriate configuration
        if service_id == None:
            services_of_node = filter(lambda x: x[SERVICE] == service_name and x[NODE_ID] == node_id, services)
            if len(services_of_node) > 0:
                return services_of_node[0]

            else:
                # Get global, discard local
                services_list = filter(lambda x: x[SERVICE] == service_name and x[SERVICE_LOCAL] == False, services)

                #Typical service_feature configuration
                if len(services_list) > 0:
                    return services_list[0]

                else:
                    logger.error("Not registered service that was requested configuration")
                    raise ERROR_NOT_REGISTERED_SERVICE
        else:

            try:
                return get_service_by_id(service_id)
            except ERROR_NOT_REGISTERED_SERVICE, e:
                logger.error("Not registered service that was requested configuration")
                raise e

def _get_configuration(service_name, service_id, config_name, node_id):
        # Check parameters
        if node_id is None or config_name is None:
            raise ERROR

        logger.info("Getting configuration for {0}/{3} {1} {2}".format(service_name, config_name, node_id, service_id))


        try:
            s = _get_service(service_name, service_id, node_id)
            return s[SERVICE_PARAMETERS][config_name]
        except Exception, e:
            raise DonCorleoneException(pack_error(e))



@app.route('/get_configuration', methods=["GET"])
def get_configuration():
    """
        Loads configuration request.

        If there is local service for given node picks it,
        if not picks  the global one (always only one!!).
    """
    try:
        logger.info("Getting configuration")

        # Get input parameters
        service_name = request.args.get('service_name')
        service_id = request.args.get('service_id')
        config_name = request.args.get('config_name')
        node_id = request.args.get('node_id')

        result = _get_configuration(service_name, service_id, config_name, node_id)

        return jsonify(result=result)

    except Exception, e:
        return jsonify(error=pack_error(e))


@app.route('/get_services', methods=['GET'])
def get_modules():
    #return json.dumps([(m[MODULE_SERVICE_NAME], modules[MODULE_ADDRESS], m[MODULE_STATUS]) for m in modules])
    return jsonify(result=services)

@app.route('/get_node_config', methods=['GET'])
def get_node_config():
    global services

    """ Check status of the jobs """
    node_id = request.args.get('node_id')
    logger.info("Checking node config for "+str(node_id))

    if node_id not in registered_nodes:
        return jsonify(error=str(ERROR_NODE_NOT_REGISTERED))

    return jsonify(result=registered_nodes[node_id])


def _terminate_node(node_id):
    # Basic error checking
    if node_id not in registered_nodes:
        return jsonify(result=str(ERROR_NODE_NOT_REGISTERED))

    logger.info("Terminating node "+node_id)

    try:
        with synchronizer:
            for m in get_node_services(node_id):
                # Try deregistering the service and delegate errror checking to _run_service
                try:
                    logger.info("Deregistering service "+m[SERVICE_ID])
                    output_run_service = _deregister_service(m[SERVICE_ID])
                    logger.info("Deregistering service "+m[SERVICE_ID]+ " "+output_run_service)
                except DonCorleoneException,e:
                    logger.error("Failed deregistering service "+m[SERVICE_ID]+" with DonCorleoneException "+str(e))
                    return jsonify(error=pack_error(e))
                except Exception,e:
                    logger.error("Failed deregistering service " + m[SERVICE_ID] + " with unexpected error "+str(e))
                    return jsonify(error=str(ERROR_FAILED_SERVICE_RUN))

        with synchronizer:
            registered_nodes.pop(node_id)

    except Exception, e:
        logger.error("Failed termination with "+str(e))
        raise e

@app.route('/terminate_node', methods=['GET'])
def terminate_node():
    """ Terminates node with all the responsibilities """
    node_id = request.args.get('node_id')



    try:
        _terminate_node(node_id)
    except Exception, e:
        return jsonify(error=pack_error(e))

    return jsonify(result=OK)



@app.route('/register_reversed', methods=['GET'])
def register_reversed():

    """
        @param service_id
        @returns [ssh user don, ssh port, ssh port don]
    """
    try:
        node_id = request.args.get("node_id")


        if not node_id in registered_nodes:
            logger.error("Failed register reversed: not registered node")
            raise ERROR_NODE_NOT_REGISTERED

        node_ssh_user = request.args.get("node_ssh_user")
        
        config = json.loads(open("config.json").read())

        ssh_user_don = config[CLIENT_CONFIG_SSH_USER]
        ssh_port_don = config[CLIENT_CONFIG_SSH_PORT]
        ssh_host_don = config[CLIENT_CONFIG_SSH_HOST]

        port = 7000

        while os.system("./scripts/test_port.sh "+str(port)) == 0:
            port += 1

        with synchronizer:
            registered_nodes[node_id].update({NODE_SSH_HOST: "127.0.0.1", NODE_SSH_PORT: port})

        return jsonify(result={"ssh-user":ssh_user_don, "ssh-port":ssh_port_don, "ssh-host":ssh_host_don, "ssh-port-redirect":port})
    except Exception, e:
        return jsonify(error=pack_error(e))



@app.route('/get_status', methods=['GET'])
def get_status():

    """
        @param service_id
        @returns status of service
    """

    service_id = request.args.get('service_id')
    print filter(lambda x: x[SERVICE_ID] == service_id, services)
    if filter(lambda x: x[SERVICE_ID] == service_id, services):
        return jsonify(result=filter(lambda x: x[SERVICE_ID] == service_name, services)[0][SERVICE_STATUS])
    else:
        return jsonify(error=str(STATUS_NOTREGISTERED))


def read_configs():
    # Read configurations
    logger.info("Reading configurations")


    ### Read in configuration files and setup default parameters ###
    for s in KNOWN_SERVICES:
        default_service_params[s] = {}
        config_file = os.path.join(CONFIG_DIRECTORY, s+".config")
        if os.path.exists(config_file):



            service_config[s] = {CONFIG_DEPENDS: [], CONFIG_ARGUMENTS: [], CONFIG_ADDS: [], CONFIG_DEFAULT_SERVICE_PARAMS: {}}

            logger.info("Reading "+s+" configuration")

            service_config[s].update(json.loads(open(config_file,"r").read()))

            if service_config[s][CONFIG_UNARY]:
                UNARY_SERVICES.add(s)
                if s in NONUNARY_SERVICES: NONUNARY_SERVICES.remove(s)
            else:
                if s in UNARY_SERVICES: UNARY_SERVICES.remove(s)
                NONUNARY_SERVICES.add(s)

            # Read in configuration
            default_service_params[s] = service_config[s][CONFIG_DEFAULT_SERVICE_PARAMS]

            ## Resolve anchors
            #for key in default_service_configs[s].iterkeys():
            #    default_service_configs[s][key] = resolve_don_value(default_service_configs[s][key], None)

            logger.info("Read service configuration")
            logger.info(s)
            logger.info(default_service_params[s])
            logger.info(service_config[s])

        else:
            logger.warn("No configuration for {0}, writing empty config (default)".format(s))
            service_config[s] = {}

@app.before_first_request
def run_daemons_flask():
    global status_checker_job_status



    if status_checker_job_status != "Running":
        read_configs()
        run_daemons()


app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    read_configs()
    run_daemons()
    app.run(port=8881, processes=3)
