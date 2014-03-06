""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.
"""

import json
import threading
import logging
import os
import subprocess

from don_corleone_exceptions import *
from utils import logger



OK = "ok"

CONFIG_SSH_PORT = "ssh-port"
CONFIG_PORT = "port"
CONFIG_HOME = "home"
CONFIG_USER = "ssh-user"


SERVICE_ODM = "odm"
SERVICE_NEO4J = "neo4j"
SERVICE_NEWS_FETCHER_MASTER = "news_fetcher_master"
SERVICE_NEWS_FETCHER = "news_fetcher"



UNARY_SERVICES = set([SERVICE_ODM, SERVICE_NEO4J, SERVICE_NEWS_FETCHER])
KNOWN_SERVICES = set([SERVICE_ODM, SERVICE_NEO4J, SERVICE_NEWS_FETCHER])

SERVICE = "service"
#Service ID is in most cases the same as SERVICE, however if it is local, or if it is multiple_slave it can differ
#For instance hadoop slaves will have service id hadoop_slave:2, whereas local service will have id
#neo4j_local, service id is basically service_name:additional_config ,where service_name can have
#additionally local tag
SERVICE_ID = "id"
SERVICE_STATUS = "status"
#Without http
SERVICE_ADDRESS = "address"
SERVICE_SSH_PORT = "ssh-port"
SERVICE_HOME = "home"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_PORT = "port"
SERVICE_USER = "user"


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
    with services_lock:
        if not filter(lambda x: x[SERVICE_ID] == service_id, services):
            return False
        else:
            if len(filter(lambda x: x[SERVICE_ID] == service_id, services)) > 1:
                logger.error("Duplicated service_id")
                exit(1)

            return filter(lambda x: x[SERVICE_ID] == service_id, services)[0]


#TODO: package as a class
def add_service(service):
    with services_lock:
        if not get_service_by_id(service[SERVICE_ID]):
            services.append(service)
            if service[SERVICE_ADDRESS] not in registered_nodes:
                node = {NODE_ADDRESS: service[SERVICE_ADDRESS], NODE_RESPONSIBILITIES: [], NODE_CONFIG: {}}
                registered_nodes[service[SERVICE_ADDRESS]] = node
            registered_nodes[service[SERVICE_ADDRESS]][NODE_RESPONSIBILITIES].append(service)
        else:
            logger.error("Error adding existing service_id")
            exit(1)

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
        if found_service[SERVICE_ADDRESS] not in registered_nodes:
            logger.error("Node not registered, fatal error")
            raise ERROR_NODE_NOT_REGISTERED
        else:
            with registered_nodes_lock:
                for id, m in enumerate(
                        registered_nodes[found_service[SERVICE_ADDRESS]][NODE_RESPONSIBILITIES]):
                    if m[SERVICE_ID] == service_id:
                        registered_nodes[found_service[SERVICE_ADDRESS]][NODE_RESPONSIBILITIES].pop(id)

        return OK

service_tmp = {"service":"odm",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"odm", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":7777,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }
service_tmp2 = {"service":"neo4j",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"neo4j", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("ocean-db.no-ip.biz"), "port":7471,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }
service_tmp3 = {"service":"neo4j",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"neo4j", "status":STATUS_TERMINATED, SERVICE_ADDRESS:get_bare_ip("192.168.0.32"), "port":7471,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }
service_tmp4 = {"service":"news_fetcher",SERVICE_SSH_PORT:22,
               SERVICE_ID:"news_fetcher", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":7777,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }


#services.append(service_tmp)
add_service(service_tmp3)
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

    prog = subprocess.Popen(["ssh {user}@{0} -p{1} ls".
                             format(
         address,
         port,
         user=user
        )], stdout=subprocess.PIPE, shell=True)

    logger.info("SSH connection "+"ssh {user}@{0} -p{1} ls".
                             format(
         address,
         port,
         user=user
        ))

    prog.communicate()

    if prog.returncode != 0:
        return (ERROR_NOT_REACHABLE_SERVICE, "")


    prog = subprocess.Popen(["ssh {user}@{0} -p{1} {2}".
                             format(address,
                                    port,
                                    cmd,
                                    user=user
                                )
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = prog.communicate()[1]

    if prog.returncode != 0:
        return (ERROR_FAILED_SSH_CMD, output)

    return (OK, output)

def update_status(m):
    with services_lock:
        logger.info("Updating status for " + str(m))
        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
                                        "./scripts/{0}_test.sh".format(m[SERVICE]))

        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Checking ssh (reachability) for ",m[SERVICE_ID], "result ", status))

        if status == ERROR_NOT_REACHABLE_SERVICE:
            remove_service(m[SERVICE_ID])
            logger.info("Service not reachable")
            return

        logger.info(("Checking server availability for ",m[SERVICE_ID], "result ", status))
        logger.info(output)

        if status == ERROR_FAILED_SSH_CMD:
            logger.error("Service terminated")
            logger.error(output)
            m[SERVICE_STATUS] = STATUS_TERMINATED
            return

        m[SERVICE_STATUS] = STATUS_RUNNING

def status_checker_job():
    global services
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
    return "Hello world!"

def _terminate_service(service_id):
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
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
                                        "./scripts/{0}_terminate.sh".format(m[SERVICE]))





        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Terminating service ",service_id, "output", output, "status ",status))

        if status == OK:
            m[SERVICE_STATUS] = STATUS_TERMINATED


        return status

def _run_service(service_id):
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
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
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
        return json.dumps(str(OK))
    except DonCorleoneException,e:
        logger.error("Failed deregistering service " + service_id + " with DonCorleoneException "+str(e))
        return json.dumps(str(e))
    except Exception,e:
        logger.error("Failed deregistering service " + service_id + " with unexpected error "+str(e))
        return json.dumps(str(ERROR))




@app.route('/register_service', methods=['POST'])
def register_service():
    try:
        output = OK
        with services_lock:
            run = json.loads(request.form['run'])
            service = json.loads(request.form['service'])
            service_id = service
            config = json.loads(request.form['config'])


            # Load default service additional config (like port configuration)
            additional_service_config = {}
            try:
                additional_service_config = json.loads(request.form['additional_config'])
            except Exception, ex:
                print request.form['additional_config']
                print str(ex)+"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"



            #TODO: add special handling for local

            if not service or not service_id or len(service)==0 or len(service_id)==0:
                return json.dumps(str(ERROR_WRONG_METHOD_PARAMETERS))

            if filter(lambda x: x[SERVICE_ID] == service_id, services):
                return json.dumps(str(ERROR_SERVICE_ID_REGISTERED))

            if filter(lambda x: x[SERVICE] == service, services) and service in UNARY_SERVICES:
                return json.dumps(str(ERROR_ALREADY_REGISTERED_SERVICE))

            if service not in KNOWN_SERVICES:
                return json.dumps(str(ERROR_NOT_RECOGNIZED_SERVICE))

            logger.info("Proceeding to registering {0} {1}".format(service, service_id))


            #Prepare service
            service_dict = {SERVICE:service,
                       SERVICE_ID:service_id,
                       SERVICE_USER:config.get(CONFIG_USER, DEFAULT_USER),
                       SERVICE_STATUS:STATUS_TERMINATED,
                       SERVICE_ADDRESS:get_bare_ip(str(request.remote_addr)),
                       SERVICE_RUN_CMD:DEFAULT_COMMAND,
                       SERVICE_SSH_PORT:config.get(CONFIG_SSH_PORT, DEFAULT_SSH_PORT),
                       SERVICE_HOME:config[CONFIG_HOME]
                       }

            service_dict.update(additional_default_options.get(service, {}))
            service_dict.update(additional_service_config)

            #Modify service_id to make it unique


            add_service(service_dict)
            registered_nodes[service_dict[SERVICE_ADDRESS]][NODE_CONFIG] = config

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


        return json.dumps(str(output))



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
        return json.dumps(str(OK))
    except DonCorleoneException,e:
        logger.error("Failed terminating service " + service_id + " with DonCorleoneException "+str(e))
        return json.dumps(str(e))
    except Exception,e:
        logger.error("Failed terminating service " + service_id + " with non expected exception "+str(e))
        return json.dumps(str(ERROR_FAILED_SERVICE_RUN))








@app.route('/run_service')
def run_service():
    service_id = request.args.get('service_id')
    global services
    """ Check status of the jobs """

    # Try running the service and delegate errror checking to _run_service
    try:
        output_run_service = _run_service(service_id)
        logger.info("Running service "+service_id+" result "+output_run_service)
        return json.dumps(str(OK))
    except DonCorleoneException,e:
        logger.error("Failed running service " + service_id + " with DonCorleoneException "+str(e))
        return json.dumps(str(e))
    except Exception,e:
        logger.error("Failed running service " + service_id + " with non expected exception "+str(e))
        return json.dumps(str(ERROR_FAILED_SERVICE_RUN))


@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    name = request.args.get('name')
    tmp = name.split("_")
    if len(tmp) == 2:
        #Typical service_feature configuration
        if filter(lambda x: x[SERVICE_ID] == tmp[0], services):
            base = filter(lambda x: x[SERVICE_ID] == tmp[0], services)[0].get(tmp[1], ERROR_NOT_RECOGNIZED_CONFIGURATION)
            if tmp[1] == SERVICE_ADDRESS and not base.startswith("http"):
                return json.dumps("http://"+base)
            else:
                return json.dumps(base)

        else:
            return json.dumps(str(ERROR_NOT_REGISTERED_SERVICE))
    else:
        return json.dumps(str(ERROR_NOT_RECOGNIZED_CONFIGURATION))


@app.route('/get_services', methods=['GET'])
def get_modules():
    #return json.dumps([(m[MODULE_SERVICE_NAME], modules[MODULE_ADDRESS], m[MODULE_STATUS]) for m in modules])
    return json.dumps(services)

@app.route('/get_node_config')
def get_node_config():
    global services
    """ Check status of the jobs """
    logger.info("Checking node config for "+str(request.remote_addr))

    address = get_bare_ip(request.remote_addr)

    if address not in registered_nodes:
        return json.dumps(str(ERROR_NODE_NOT_REGISTERED))


    return json.dumps(registered_nodes[address])


@app.route('/terminate_node')
def terminate_node():
    """ Terminates node with all the responsibilities """
    address = get_bare_ip(request.remote_addr)

    logger.info("Terminating node "+str(address))

    # Basic error checking
    if address not in registered_nodes:
        return json.dumps(str(ERROR_NODE_NOT_REGISTERED))



    try:
        with services_lock:
            for m in services:
                # Try deregistering the service and delegate errror checking to _run_service
                try:
                    logger.info("Deregistering service "+m[SERVICE_ID])
                    output_run_service = _deregister_service(m[SERVICE_ID])
                    logger.info("Deregistering service "+m[SERVICE_ID]+ " "+output_run_service)
                except DonCorleoneException,e:
                    logger.error("Failed deregistering service "+m[SERVICE_ID]+" with DonCorleoneException "+str(e))
                    return json.dumps(str(e))
                except Exception,e:
                    logger.error("Failed deregistering service " + m[SERVICE_ID] + " with unexpected error "+str(e))
                    return json.dumps(str(ERROR_FAILED_SERVICE_RUN))

        with registered_nodes_lock:
            registered_nodes.pop(address)

    except Exception, e:
        logger.error("Failed termination with "+str(e))
        return json.dumps(str(ERROR))

    return json.dumps(str(OK))


@app.route('/get_status', methods=['GET'])
def get_status():
    service_name = request.args.get('service_id')
    print filter(lambda x: x[SERVICE_ID] == service_name, services)
    if filter(lambda x: x[SERVICE_ID] == service_name, services):
        return filter(lambda x: x[SERVICE_ID] == service_name, services)[0][SERVICE_STATUS]
    else:
        return json.dumps(str(STATUS_NOTREGISTERED))



@app.before_first_request
def run_daemons_flask():
    global status_checker_job_status
    if status_checker_job_status != "Running":
        run_daemons()


app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    run_daemons()
    app.run(port=8881)