""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.


Protocol: JSONP:
    {
        result: JSON(data)
    }



Services are added and not tested for accessibility first time. Services are added
to service list which is periodically updated (terminated/running) status
TODO: Testing server accessibiliy (ping) and terminating it if not accesible


"""

#TODO: timeout for ssh

import json

import threading
import logging
import os
import subprocess

from don_corleone_exceptions import *
from don_utils import logger

from flask.ext.jsonpify import jsonify


OK = "ok"

CONFIG_PORT = "port"
CONFIG_HOME = "home"
CONFIG_SSH_USER = "ssh-user"
CONFIG_SSH_HOST = "public_ssh_domain"
CONFIG_SSH_PORT = "ssh-port"


SERVICE_ODM = "odm"
SERVICE_LIONFISH = "lionfish"
SERVICE_ZOOKEEPER = "zookeeper"
SERVICE_KAFKA = "kafka"
SERVICE_NEO4J = "neo4j"
SERVICE_NEWS_FETCHER_MASTER = "news_fetcher_master"
SERVICE_NEWS_FETCHER = "news_fetcher"
SERVICE_SPIDERCRAB_MASTER = "spidercrab_master"
SERVICE_SPIDERCRAB_SLAVE = "spidercrab_slave"



UNARY_SERVICES = set([SERVICE_ODM, SERVICE_LIONFISH, SERVICE_NEO4J, SERVICE_NEWS_FETCHER, SERVICE_ZOOKEEPER, SERVICE_KAFKA, SERVICE_SPIDERCRAB_MASTER, SERVICE_SPIDERCRAB_SLAVE])
KNOWN_SERVICES = set([SERVICE_ODM, SERVICE_LIONFISH,  SERVICE_NEO4J, SERVICE_NEWS_FETCHER, SERVICE_KAFKA, SERVICE_ZOOKEEPER, SERVICE_SPIDERCRAB_MASTER, SERVICE_SPIDERCRAB_SLAVE])

SERVICE = "service"
#Service ID is in most cases the same as SERVICE, however if it is local, or if it is multiple_slave it can differ
#For instance hadoop slaves will have service id hadoop_slave:2, whereas local service will have id
#neo4j_local, service id is basically service_name:additional_config ,where service_name can have
#additionally local tag
SERVICE_ID = "service_id"
SERVICE_STATUS = "status"
#Without http
SERVICE_HOME = "home"
SERVICE_PORT = "port"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_NAME = "service"
SERVICE_CONFIG = "service_config" # Additional service config
NODE_ID = "node_id" # Id for node
SERVICE_LOCAL = "local"


#Nodes in the system
#Each node is "config" + "services"
registered_nodes = {}
NODE_RESPONSIBILITIES = "node_responsibilities"
NODE_ADDRESS = "node_address"
NODE_CONFIG = "node_config"
NODE_SSH_HOST = "node_ssh_host"
NODE_SSH_PORT = "node_ssh_port"
NODE_SSH_USER = "node_ssh_user"


additional_default_options = {}
additional_default_options[SERVICE_ODM] = {SERVICE_PORT: 7777}
additional_default_options[SERVICE_NEO4J] = {SERVICE_PORT: 7474}


DEFAULT_COMMAND = "default"
DEFAULT_SSH_PORT = 22
DEFAULT_USER = "ocean"

STATUS_NOTREGISTERED = "not_registered"
STATUS_TERMINATED = "terminated"
STATUS_RUNNING = "running"


services_lock = threading.RLock()
registered_nodes_lock = threading.RLock()
services = []


status_checker_job_status = "NotRunning"




import socket

def get_bare_ip(address):
    """ Return bare ip for address (ip->ip, domain -> ip) """
    address = str(address)
    try:
        return address if address[0].isdigit() else socket.gethostbyname(address)
    except Exception,e:
        logger.error("Error running get_bare_ip")
        logger.error(str(e))
        return address

#TODO: package as a class
def get_service_by_id(service_id):
    """ Returns service given service_id """
    with services_lock:
        if not filter(lambda x: x[SERVICE_ID] == service_id, services):
            return False
        else:
            if len(filter(lambda x: x[SERVICE_ID] == service_id, services)) > 1:
                logger.error("Duplicated service_id")
                exit(1)

            result = filter(lambda x: x[SERVICE_ID] == service_id, services)[0]
    return result

def get_node_services(node_id):
    """ Returns service of given node_id"""
    with services_lock:
        # Return is fine in with clause
        return [s for s in services if s[NODE_ID] == node_id]

#TODO: package as a class
def add_service(service):
    """ Adds service """
    with services_lock:
        # Check if no duplicate or duplicate and local
        if not get_service_by_id(service[SERVICE_ID]) or service[SERVICE_LOCAL]:

            # Check if local then only one local
            if any([True for s in services if s[SERVICE] == service[SERVICE] and s[NODE_ID] == service[NODE_ID]]):
                raise ERROR_DUPLICATE

            services.append(service)

            registered_nodes[service[NODE_ID]][NODE_RESPONSIBILITIES].append(service)
        else:
            logger.error("Error adding existing service_id")
            raise ERROR_DUPLICATE



#TODO: package as a class
def remove_service(service_id):
    """ Removes service from registered services """
    with services_lock:
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
            with registered_nodes_lock:
                for id, m in enumerate(
                        registered_nodes[found_service[NODE_ID]][NODE_RESPONSIBILITIES]):
                    if m[SERVICE_ID] == service_id:
                        registered_nodes[found_service[NODE_ID]][NODE_RESPONSIBILITIES].pop(id)

        return OK


import time





#TODO: add throwing errors here
def cautious_run_cmd_over_ssh(cmd, node_id):
    """ 
        Returns appropriate errors if encounters problems
        @note Doesn't throw errors
    """

    
    n = registered_nodes[node_id]
    user, port, host = n[NODE_SSH_USER], n[NODE_SSH_PORT], n[NODE_SSH_HOST]

    # oStrictHostKeyChecking - sdisables asking for RSA key
    cmd = "ssh -oStrictHostKeyChecking=no {user}@{0} -p{1} -o ConnectTimeout=2 {2}".\
                             format(host,\
                                    port,\
                                    cmd,\
                                    user=user\
                                )

    logger.info("Running ssh command: "+str(cmd))

    prog = subprocess.Popen([cmd
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = prog.communicate()

    logger.info(output)

    if prog.returncode != 0:
        logger.info("Error running command " + str(ERROR_FAILED_SSH_CMD))
        return (ERROR_FAILED_SSH_CMD, output)

    return (OK, output)

def update_status(m):
    """ Checks and updates status of given service  """
    logger.info("Updating status for " + str(m))
    cmd = "\"(cd {0} && {1})\"".format(
                                    os.path.join(m[SERVICE_HOME],"don_corleone"),
                                    "./scripts/{0}_test.sh".format(m[SERVICE]))

    status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID])

    logger.info(("Checking ssh (reachability) for ",m[SERVICE_ID], "result ", str(status)))

    with services_lock:
        
        # Not removing 
        """
        if status == ERROR_NOT_REACHABLE_SERVICE:
            remove_service(m[SERVICE_ID])
            logger.info("Service not reachable")
            return
        """

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
        time.sleep(10)


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
    with services_lock:
        if not get_service_by_id(service_id):
            raise ERROR_NOT_REGISTERED_SERVICE

        m = get_service_by_id(service_id)

        if m[SERVICE_STATUS] == STATUS_TERMINATED:
            return OK

        if m[SERVICE_STATUS] != STATUS_RUNNING:
            logger.error("Wrong service status")
            exit(1)


        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"don_corleone"),
                                        "./scripts/{0}_terminate.sh".format(m[SERVICE]))

    status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID])


    with services_lock:
        logger.info(("Terminating service ",service_id, "output", output, "status ",status))

        if status == OK:
            m[SERVICE_STATUS] = STATUS_TERMINATED


        return status

def _run_service(service_id):
    """ Run service given service_id
        @returns OK or DonCorleone exception
    """
    with services_lock:
        if not get_service_by_id(service_id):
            raise ERROR_NOT_REGISTERED_SERVICE

        m = get_service_by_id(service_id)

        if m[SERVICE_STATUS] == STATUS_RUNNING:
            raise ERROR_SERVICE_ALREADY_RUNNING

        if m[SERVICE_STATUS] != STATUS_TERMINATED:
            logger.error("Wrong service status")
            exit(1)


        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"don_corleone"),
                                        "./scripts/run.sh {1} ./scripts/{0}_run.sh".format(m[SERVICE], m[SERVICE_ID]))



    status, output = cautious_run_cmd_over_ssh(cmd, m[NODE_ID])




    with services_lock:
        logger.info(("Running service ",service_id, "output", output, "status ",status))
    
    update_status(m)

    """
        # Update status
        if status == OK:
            m[SERVICE_STATUS] = STATUS_RUNNING
        else:
            # If status is undetermined set it to terminated, checking status daemon should check it further
            m[SERVICE_STATUS] = STATUS_TERMINATED # Maybe even deregistered?
    """


    return status

def _deregister_service(service_id):
    """ Deregister service given service_id
        @returns OK or DonCorleone exception
    """
    with services_lock:

        #TODO: add special handling for local
        if not get_service_by_id(service_id):
            raise ERROR_NOT_REGISTERED_SERVICE

        if len(filter(lambda x: x[SERVICE_ID] == service_id, services)) > 1:
            logger.error("Duplicated service id")
            raise ERROR

        logger.info("Terminating service")
        _terminate_service(service_id)
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
        return jsonify(result=str(e))
    except Exception,e:
        logger.error("Failed deregistering service " + service_id + " with unexpected error "+str(e))
        return jsonify(result=str(ERROR))

#q - ma wplyw : q-->0 : liczymy nie zerowe, q-->inf : rownomierne





from flask import Response
@app.route('/register_node', methods=['POST'])
def register_node():
    try:
        output = OK
        with services_lock:
            config = json.loads(request.form['config'])
            node_id = json.loads(request.form['node_id'])

            with registered_nodes_lock:
                if not node_id in registered_nodes:
                    node = {NODE_ID:node_id, NODE_ADDRESS:config[CONFIG_SSH_HOST],NODE_CONFIG:config, NODE_RESPONSIBILITIES:[], NODE_SSH_HOST:config[CONFIG_SSH_HOST],
                    NODE_SSH_PORT:config[CONFIG_SSH_PORT], NODE_SSH_USER:config[CONFIG_SSH_USER]
                    }
                    registered_nodes[node_id] = node
            
            output=OK


        return jsonify(result=str(output))

    except Exception, e:
        logger.error("Failed registering node with "+str(e))
        return jsonify(result=str(e))


   


@app.route('/register_service', methods=['POST'])
def register_service():
    try:
        output = OK
        with services_lock:
            run = json.loads(request.form['run'])
            service_name = json.loads(request.form['service'])
            public_url = json.loads(request.form['public_url'])
            config = json.loads(request.form['config'])


            # Load default service additional config (like port configuration)
            additional_service_config = additional_default_options.get(service_name, {})
            try:
                additional_service_config = json.loads(request.form['additional_config'])
            except Exception, ex:
                print request.form['additional_config']
                print str(ex)+"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

            node_id = json.loads(request.form['node_id'])

            with registered_nodes_lock:
                if not node_id in registered_nodes:
                    raise ERROR_NOT_REGISTERED_NODE

            local = True if 'local' in request.form or additional_service_config.get('local', False)\
                else False

            logger.info("Registering local="+str(local)+" service")


            #Prepare service id
            services_ids = [int(s[SERVICE_ID].split("_")[1]) for s in services if s[SERVICE] == service_name]
            next_id = max(services_ids)+1 if len(services_ids) else 1
            service_id = service_name + "_" + str(next_id)





            if not service_name or not service_id or len(service_name)==0 or len(service_id)==0:
                return jsonify(result=str(ERROR_WRONG_METHOD_PARAMETERS))

            # No duplicated service id
            if filter(lambda x: x[SERVICE_ID] == service_id, services):
                return jsonify(result=str(ERROR_SERVICE_ID_REGISTERED))

            # Only one global service
            if filter(lambda x: x[SERVICE] == service_name and x[SERVICE_LOCAL]==False, services) and (service_name in UNARY_SERVICES) and (local is False):
                return jsonify(result=str(ERROR_ALREADY_REGISTERED_SERVICE))

            # Not known service..
            if service_name not in KNOWN_SERVICES:
                return jsonify(result=str(ERROR_NOT_RECOGNIZED_SERVICE))

            logger.info("Proceeding to registering {0} {1}".format(service_name, service_id))


    

            #Prepare service
            service_dict = {SERVICE:service_name,
                       SERVICE_ID:service_id,
                       SERVICE_STATUS:STATUS_TERMINATED,
                       NODE_ID: node_id,
                       NODE_ADDRESS: public_url,
                       SERVICE_LOCAL: local,
                       SERVICE_RUN_CMD:DEFAULT_COMMAND,
                       SERVICE_HOME:config[CONFIG_HOME],
                       SERVICE_CONFIG: additional_service_config
                       }


            #Modify service_id to make it unique


            add_service(service_dict)

            logger.info(("Registering " if not run else "Running and registering ")+str(service_dict))

            logger.info("Running service "+service_id)

            update_status(service_dict)

            if run:
                service_id = service_dict[SERVICE_ID]
                try:
                    output_run_service = _run_service(service_dict[SERVICE_ID])
                    logger.info("Running service "+service_dict[SERVICE_ID]+" result "+output_run_service)
                except DonCorleoneException,e:
                    logger.error("Failed deregistering service " + service_id + " with DonCorleoneException "+str(e))
                    output = e
                except Exception,e:
                    logger.error("Failed deregistering service " + service_id + " with non expected exception "+str(e))
                    output = ERROR_FAILED_SERVICE_RUN

                if service_dict[SERVICE_STATUS] != STATUS_RUNNING:
                    output = ERROR_FAILED_SERVICE_RUN
                else:
                    output = OK
            else:
                output=OK


        return jsonify(result=str(output))



    except Exception, e:
        logger.error("Failed registering with "+str(e))
        return jsonify(result=str(e))



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
        return jsonify(result=str(e))
    except Exception,e:
        logger.error("Failed terminating service " + service_id + " with non expected exception "+str(e))
        return jsonify(result=str(ERROR_FAILED_SERVICE_RUN))








@app.route('/run_service')
def run_service():
    service_id = request.args.get('service_id')
    global services
    """ Check status of the jobs """

    # Try running the service and delegate errror checking to _run_service
    try:
        output_run_service = _run_service(service_id)
        logger.info("Running service "+service_id+" result "+output_run_service)
        return jsonify(result=str(OK))
    except DonCorleoneException,e:
        logger.error("Failed running service " + service_id + " with DonCorleoneException "+str(e))
        return jsonify(result=json.dumps(str(e)))
    except Exception,e:
        logger.error("Failed running service " + service_id + " with non expected exception "+str(e))
        return jsonify(result=json.dumps(str(ERROR_FAILED_SERVICE_RUN)))



import flask

@app.route('/get_services')
def get_services():
    with services_lock:
        return jsonify(result=services)

@app.route('/get_nodes')
def get_nodes():
    with registered_nodes_lock:
        return jsonify(result=registered_nodes)


@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    """
        Loads configuration request.

        If there is local service for given node picks it,
        if not picks  the global one (always only one!!).
    """

    # Get input parameters
    service_name = request.args.get('service_name')
    config_name = request.args.get('config_name')
    node_id = request.args.get('node_id')

    logger.info("Getting configuration for {0} {1} {2}".format(service_name, config_name, node_id))

    services_of_node = filter(lambda x: x[SERVICE] == service_name and x[NODE_ID] == node_id, services)
    if len(services_of_node) > 0:
        # Try getting value
        try:
            config_value = services_of_node[0][SERVICE_CONFIG][config_name]
            return jsonify(result=config_value)
        except Exception, e:
	    logger.error("Found service of given node - local or not, but missed configuration")
            return jsonify(result=(str(ERROR_NOT_RECOGNIZED_CONFIGURATION)))

    else:
        # Get global, discard local
        services_list = filter(lambda x: x[SERVICE] == service_name and x[SERVICE_LOCAL] == False, services)

        #Typical service_feature configuration
        if len(services_list) > 0:
            try:
                config_value = services_list[0][SERVICE_CONFIG][config_name]
                return jsonify(result=config_value)
            except Exception, e:
		logger.error(services_list[0][SERVICE_CONFIG])
	    	logger.error("Found global service, but missed configuration")
                return jsonify(result=(str(ERROR_NOT_RECOGNIZED_CONFIGURATION)))

        else:
            return jsonify(result=str(ERROR_NOT_REGISTERED_SERVICE))





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
        return jsonify(result=str(ERROR_NODE_NOT_REGISTERED))


    return jsonify(result=registered_nodes[node_id])


@app.route('/terminate_node', methods=['GET'])
def terminate_node():
    """ Terminates node with all the responsibilities """
    node_id = request.args.get('node_id')


    logger.info("Terminating node "+node_id)

    # Basic error checking
    if node_id not in registered_nodes:
        return jsonify(result=str(ERROR_NODE_NOT_REGISTERED))



    try:
        with services_lock:
            for m in get_node_services(node_id):
                # Try deregistering the service and delegate errror checking to _run_service
                try:
                    logger.info("Deregistering service "+m[SERVICE_ID])
                    output_run_service = _deregister_service(m[SERVICE_ID])
                    logger.info("Deregistering service "+m[SERVICE_ID]+ " "+output_run_service)
                except DonCorleoneException,e:
                    logger.error("Failed deregistering service "+m[SERVICE_ID]+" with DonCorleoneException "+str(e))
                    return jsonify(result=str(e))
                except Exception,e:
                    logger.error("Failed deregistering service " + m[SERVICE_ID] + " with unexpected error "+str(e))
                    return jsonify(result=str(ERROR_FAILED_SERVICE_RUN))

        with registered_nodes_lock:
            registered_nodes.pop(node_id)

    except Exception, e:
        logger.error("Failed termination with "+str(e))
        return jsonify(result=str(ERROR))

    return jsonify(result=OK)



@app.route('/register_reversed', methods=['GET'])
def register_reversed():

    """
        @param service_id
        @returns [ssh user don, ssh port, ssh port don]
    """

    node_id = request.args.get("node_id")


    if not node_id in registered_nodes:
        logger.error("Failed register reversed: not registered node")
        return jsonify(result=str(ERROR_NODE_NOT_REGISTERED))

    node_ssh_user = request.args.get("node_ssh_user")
    
    config = json.loads(open("config.json").read())

    ssh_user_don = config[CONFIG_SSH_USER]  
    ssh_port_don = config[CONFIG_SSH_PORT]
    ssh_host_don = config[CONFIG_SSH_HOST]

    port = 7000

    while os.system("./scripts/test_port.sh "+str(port)) == 0:
        port += 1

    with registered_nodes_lock:
        registered_nodes[node_id].update({NODE_SSH_HOST: "127.0.0.1", NODE_SSH_PORT: port})

    return jsonify(result={"ssh-user":ssh_user_don, "ssh-port":ssh_port_don, "ssh-host":ssh_host_don, "ssh-port-redirect":port})




@app.route('/get_status', methods=['GET'])
def get_status():

    """
        @param service_id
        @returns status of service
    """

    service_name = request.args.get('service_id')
    print filter(lambda x: x[SERVICE_ID] == service_name, services)
    if filter(lambda x: x[SERVICE_ID] == service_name, services):
        return jsonify(result=filter(lambda x: x[SERVICE_ID] == service_name, services)[0][SERVICE_STATUS])
    else:
        return jsonify(result=STATUS_NOTREGISTERED)



@app.before_first_request
def run_daemons_flask():
    global status_checker_job_status
    if status_checker_job_status != "Running":
        run_daemons()


app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    run_daemons()
    app.run(port=8881)
