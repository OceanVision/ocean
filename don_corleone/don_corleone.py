""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.


Protocol: JSONP:
    {
        result: JSON(data)
    }




"""

#TODO: timeout for ssh

import json

import threading
import logging
import os
import subprocess

from don_corleone_exceptions import *
from utils import logger

from flask.ext.jsonpify import jsonify


OK = "ok"

CONFIG_SSH_PORT = "ssh-port"
CONFIG_PORT = "port"
CONFIG_HOME = "home"
CONFIG_USER = "ssh-user"


SERVICE_ODM = "odm"
SERVICE_LIONFISH = "lionfish"
SERVICE_NEO4J = "neo4j"
SERVICE_NEWS_FETCHER_MASTER = "news_fetcher_master"
SERVICE_NEWS_FETCHER = "news_fetcher"



UNARY_SERVICES = set([SERVICE_ODM, SERVICE_LIONFISH, SERVICE_NEO4J, SERVICE_NEWS_FETCHER])
KNOWN_SERVICES = set([SERVICE_ODM, SERVICE_LIONFISH,  SERVICE_NEO4J, SERVICE_NEWS_FETCHER])

SERVICE = "service"
#Service ID is in most cases the same as SERVICE, however if it is local, or if it is multiple_slave it can differ
#For instance hadoop slaves will have service id hadoop_slave:2, whereas local service will have id
#neo4j_local, service id is basically service_name:additional_config ,where service_name can have
#additionally local tag
SERVICE_ID = "service_id"
SERVICE_STATUS = "status"
#Without http
SERVICE_ADDRESS = "address"
SERVICE_SSH_PORT = "ssh-port"
SERVICE_HOME = "home"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_NAME = "service"
SERVICE_PORT = "port"
SERVICE_USER = "user"
NODE_ID = "node_id" # Id for node
SERVICE_LOCAL = "local"


#Nodes in the system
#Each node is "config" + "services"
registered_nodes = {}
NODE_RESPONSIBILITIES = "node_responsibilities"
NODE_ADDRESS = "node_address"
NODE_CONFIG = "node_config"


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

            if service[NODE_ID] not in registered_nodes:
                node = {NODE_ID: service[NODE_ID], NODE_ADDRESS: service[SERVICE_ADDRESS], NODE_RESPONSIBILITIES: [], NODE_CONFIG: {}}
                registered_nodes[service[NODE_ID]] = node
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


### Exemplary data ###

service_tmp = {SERVICE_NAME:"odm",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"odm", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":7777,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER,
               NODE_ID: "acer"
               }
service_tmp2 = {SERVICE_NAME:"neo4j",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"neo4j", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("ocean-db.no-ip.biz"), "port":7471,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER,
               NODE_ID: "acer"
               }
service_tmp3 = {SERVICE_NAME:"neo4j",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"neo4j", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("192.168.0.32"), "port":7471,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER,
               NODE_ID: "acer"
               }
service_tmp4 = {SERVICE_NAME:"news_fetcher",SERVICE_SSH_PORT:22,
               SERVICE_ID:"news_fetcher", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":7777,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER,
               NODE_ID: "acer"
               }

#Local neo4j
service_tmp5 = {SERVICE_NAME:"neo4j",SERVICE_SSH_PORT:22,
               SERVICE_ID:"neo4j_1", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("127.0.0.1"), "port":7471,
               "home":"/home/moje/Projekty/ocean/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:"staszek",
               NODE_ID: "staszek"
               }

service_tmp6 = {SERVICE_NAME:"odm",SERVICE_SSH_PORT:221,
               SERVICE_ID:"odm_1", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("127.0.0.1"), "port":7471,
               "home":"/home/moje/Projekty/ocean/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:"staszek",
               NODE_ID: "staszek"
               }


service_tmp7 = {SERVICE_NAME:"odm",SERVICE_SSH_PORT:222,
               SERVICE_ID:"odm_2", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("127.0.0.1"), "port":74721,
               "home":"/home/moje/Projekty/ocean/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:"staszek",
               NODE_ID: "staszek2"
               }

#services.append(service_tmp)
#add_service(service_tmp5)
#add_service(service_tmp6)
#add_service(service_tmp7)
#services.append(service_tmp4)

"""
Each module is represented as a dictionary with fields:

* name
* service_name
* ip/domain
* port
* home_folder
* pid
* status

"""

import time






def cautious_run_cmd_over_ssh(user, port, cmd, address):
    """ Returns appropriate errors if encounters problems """

    prog = subprocess.Popen(["ssh {user}@{0} -p{1} -o ConnectTimeout=1 ls".
                             format(
         address,
         port,
         user=user
        )], stdout=subprocess.PIPE, shell=True)

    logger.info("SSH connection "+"ssh {user}@{0} -o ConnectTimeout=1 -p{1} ls".
                             format(
         address,
         port,
         user=user
        ))

    prog.communicate()

    if prog.returncode != 0:
        logger.info("Error running command " + str(ERROR_FILE_NOT_FOUND))
        return (ERROR_NOT_REACHABLE_SERVICE, "")


    prog = subprocess.Popen(["ssh {user}@{0} -p{1} -o ConnectTimeout=1 {2}".
                             format(address,
                                    port,
                                    cmd,
                                    user=user
                                )
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = prog.communicate()[1]

    if prog.returncode != 0:
        logger.info("Error running command " + str(ERROR_FAILED_SSH_CMD))
        return (ERROR_FAILED_SSH_CMD, output)

    return (OK, output)

def update_status(m):
    """ Checks and updates status of given service  """
    with services_lock:
        logger.info("Updating status for " + str(m))
        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"don_corleone"),
                                        "./scripts/{0}_test.sh".format(m[SERVICE]))

        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Checking ssh (reachability) for ",m[SERVICE_ID], "result ", str(status)))

        if status == ERROR_NOT_REACHABLE_SERVICE:
            remove_service(m[SERVICE_ID])
            logger.info("Service not reachable")
            return

        logger.info(("Checking server availability for ",m[SERVICE_ID], "result ", str(status)))
        logger.info(output)

        if status == ERROR_FAILED_SSH_CMD:
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


@app.route('/')
def hello():
    return flask.render_template("index.html")

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





        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

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




        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Running service ",service_id, "output", output, "status ",status))

        # Update status
        if status == OK:
            m[SERVICE_STATUS] = STATUS_RUNNING
        else:
            # If status is undetermined set it to terminated, checking status daemon should check it further
            m[SERVICE_STATUS] = STATUS_TERMINATED # Maybe even deregistered?



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



from flask import Response
@app.route('/register_service', methods=['POST'])
def register_service():
    try:
        output = OK
        with services_lock:
            run = json.loads(request.form['run'])
            service_name = json.loads(request.form['service'])

            # Load default service additional config (like port configuration)
            additional_service_config = {}
            try:
                additional_service_config = json.loads(request.form['additional_config'])
            except Exception, ex:
                print request.form['additional_config']
                print str(ex)+"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

            node_id = json.loads(request.form['node_id'])
            local = True if 'local' in request.form or 'local' in additional_service_config\
                else False

            #Prepare service id
            services_ids = [int(s[SERVICE_ID].split("_")[1]) for s in services if s[SERVICE] == service_name]
            next_id = max(services_ids)+1 if len(services_ids) else 1
            service_id = service_name + "_" + str(next_id)


            config = json.loads(request.form['config'])





            if not service_name or not service_id or len(service_name)==0 or len(service_id)==0:
                return jsonify(result=str(ERROR_WRONG_METHOD_PARAMETERS))

            if filter(lambda x: x[SERVICE_ID] == service_id, services):
                return jsonify(result=str(ERROR_SERVICE_ID_REGISTERED))

            if filter(lambda x: x[SERVICE] == service_name, services) and service_name in UNARY_SERVICES:
                return jsonify(result=str(ERROR_ALREADY_REGISTERED_SERVICE))

            if service_name not in KNOWN_SERVICES:
                return jsonify(result=str(ERROR_NOT_RECOGNIZED_SERVICE))

            logger.info("Proceeding to registering {0} {1}".format(service_name, service_id))


            #Prepare service
            service_dict = {SERVICE:service_name,
                       SERVICE_ID:service_id,
                       SERVICE_USER:config.get(CONFIG_USER, DEFAULT_USER),
                       SERVICE_STATUS:STATUS_TERMINATED,
                       NODE_ID: node_id,
                       SERVICE_LOCAL: local,
                       SERVICE_ADDRESS:get_bare_ip(str(request.remote_addr)),
                       SERVICE_RUN_CMD:DEFAULT_COMMAND,
                       SERVICE_SSH_PORT:config.get(CONFIG_SSH_PORT, DEFAULT_SSH_PORT),
                       SERVICE_HOME:config[CONFIG_HOME]
                       }

            service_dict.update(additional_default_options.get(service_name, {}))
            service_dict.update(additional_service_config)

            #Modify service_id to make it unique


            add_service(service_dict)
            registered_nodes[service_dict[NODE_ID]][NODE_CONFIG] = config

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
        return "error"



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
            config_value = services_of_node[0][config_name]
            return jsonify(result=config_value)
        except Exception, e:
            return jsonify(result=(str(ERROR_NOT_RECOGNIZED_CONFIGURATION)))

    else:
        services_list = filter(lambda x: x[SERVICE] == service_name, services)

        #Typical service_feature configuration
        if len(services_list) > 0:
            try:
                config_value = services_list[0][config_name]
                return jsonify(result=json.config_value)
            except Exception, e:
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
    address = get_bare_ip(request.remote_addr)
    node_id = request.args.get('node_id')


    logger.info("Terminating node "+str(address))

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
