""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.
"""

import json
import threading
import logging
import os
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False



ERROR_NOT_RUNNING_SERVICE = "error_not_running_service_error"
ERROR_ALREADY_REGISTERED_SERVICE = "error_already_registered_service"
ERROR_ALREADY_EXISTING_SERVICE = "error_already_existing_service"
ERROR_NOT_REGISTERED_SERVICE = "error_not_registered_service_error"
ERROR_NOT_RECOGNIZED_CONFIGURATION = "error_not_recognized_configuration"
ERROR_NOT_REACHABLE_SERVICE = "error_not_reachable_service"
ERROR_FAILED_SERVICE_RUN = "error_failed_service_run"
ERROR_FAILED_SSH_CMD = "error_failed_ssh_cmd"
ERROR_SERVICE_ALREADY_RUNNING = "error_service_already_running"
ERROR_SERVICE_ALREADY_TERMINATED= "error_service_already_terminated"
ERROR_NOT_RECOGNIZED_SERVICE = "error_not_recognized_service"
ERROR_SERVICE_ID_REGISTERED = "error_service_id_registered"
ERROR_WRONG_METHOD_PARAMETERS = "error_wrong_method_parameters"
OK = "ok"

CONFIG_SSH_PORT = "ssh-port"
CONFIG_PORT = "port"
CONFIG_HOME = "home"
CONFIG_USER = "ssh-user"

SERVICE_ODM = "odm"
SERVICE_NEO4J = "neo4j"
#SERVICE_NEWS_FETCHER_MASTER = "news_fetcher_master"
SERVICE_NEWS_FETCHER = "news_fetcher"
UNARY_SERVICES = set([SERVICE_ODM, SERVICE_NEO4J, SERVICE_NEWS_FETCHER])
KNOWN_SERVICES = set([SERVICE_ODM, SERVICE_NEO4J, SERVICE_NEWS_FETCHER])

SERVICE = "service"
SERVICE_ID = "id"
SERVICE_STATUS = "status"
SERVICE_ADDRESS = "address"
SERVICE_SSH_PORT = "ssh-port"
SERVICE_HOME = "home"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_USER = "user"

DEFAULT_COMMAND = "default"
DEFAULT_SSH_PORT = 22
DEFAULT_USER = "ocean"

STATUS_NOTREGISTERED = "not_registered"
STATUS_TERMINATED = "terminated"
STATUS_RUNNING = "running"


services_lock = threading.RLock()
services = []


service_tmp = {"service":"odm",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"odm", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":2231,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }
service_tmp2 = {"service":"neo4j",SERVICE_SSH_PORT:2231,
               SERVICE_ID:"neo4j", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":2231,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }

service_tmp4 = {"service":"news_fetcher",SERVICE_SSH_PORT:22,
               SERVICE_ID:"news_fetcher", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":7777,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: DEFAULT_COMMAND, SERVICE_USER:DEFAULT_USER
               }


#services.append(service_tmp)
services.append(service_tmp2)
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

# Index used to identify slaves (news_fetcher, web_crawler)
slave_index = 0



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

def update_status(id, m):
    with services_lock:
        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
                                        "./scripts/{0}_test.sh".format(m[SERVICE]))

        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Checking ssh (reachability) for ",m[SERVICE_ID], "result ", status))

        if status == ERROR_NOT_REACHABLE_SERVICE:
            if id: services.remove(id)
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
        time.sleep(10)
        for id, m in enumerate(services):
            update_status(id, m)


### Flask module ###

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
app = Flask(__name__)

#@app.before_first_request
def run_daemons():
    t = threading.Thread(target=status_checker_job)
    t.daemon = True
    t.start()



@app.route('/')
def hello():
    return "Hello world!"


@app.route('/register_service', methods=['POST'])
def register_service():
    output = json.dumps(OK)
    with services_lock:

        print request.form

        service_id = request.form['service_id']
        service = request.form['service']


        config = json.loads(request.form['config'])


        print "Proceeding"
        additional_service_config = {}
        try:
            additional_service_config = json.loads(request.form['additional_config'])
        except Exception, ex:
            print request.form['additional_config']
            print str(ex)+"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        print len(additional_service_config)
        print "Proceeding"

        if not service or not service_id or len(service)==0 or len(service_id)==0:
            return json.dumps(ERROR_WRONG_METHOD_PARAMETERS)

        if filter(lambda x: x[SERVICE_ID] == service_id, services):
            return json.dumps(ERROR_SERVICE_ID_REGISTERED)

        if filter(lambda x: x[SERVICE] == service, services) and service in UNARY_SERVICES:
            return json.dumps(ERROR_ALREADY_REGISTERED_SERVICE)

        if service not in KNOWN_SERVICES:
            return json.dumps(ERROR_NOT_RECOGNIZED_SERVICE)

        logger.info("Proceeding to registering {0} {1}".format(service, service_id))


        service = {SERVICE:service,
                   SERVICE_ID:service_id,
                   SERVICE_USER:config.get(CONFIG_USER, DEFAULT_USER),
                   SERVICE_STATUS:STATUS_TERMINATED,
                   SERVICE_ADDRESS:request.remote_addr,
                   SERVICE_RUN_CMD:DEFAULT_COMMAND,
                   SERVICE_SSH_PORT:config.get(CONFIG_SSH_PORT, DEFAULT_SSH_PORT),
                   SERVICE_HOME:config[CONFIG_HOME]
                   }

        service.update(additional_service_config)

        services.append(service)

        logger.info("Registering "+str(service))

        logger.info("Running service "+service_id)

        update_status(None, service)

        output_run_service = _run_service(service[SERVICE_ID])



        if output_run_service != json.dumps(OK):
            logger.error("Failed starting service")
            logger.info("Running service output = "+str(output))

        if service[SERVICE_STATUS] != STATUS_RUNNING:
            output = output_run_service
        else:
            output = OK



    return OK


def _terminate_service(service_id):
    with services_lock:
        if not filter(lambda x: x[SERVICE_ID] == service_id, services):
            return json.dumps(ERROR_NOT_REGISTERED_SERVICE)

        m = filter(lambda x: x[SERVICE_ID] == service_id, services)[0]

        if m[SERVICE_STATUS] == STATUS_TERMINATED:
            return json.dumps(ERROR_SERVICE_ALREADY_TERMINATED)

        if m[SERVICE_STATUS] != STATUS_RUNNING:
            logger.error("Wrong service status")
            exit(1)


        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
                                        "./scripts/{0}_terminate.sh".format(m[SERVICE]))

        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Terminating service ",service_id, "output", output, "status ",status))

        return json.dumps(status)

@app.route('/terminate_service')
def terminate_service():
    service_id = request.args.get('service_id')
    global services
    """ Check status of the jobs """
    return _terminate_service(service_id)



def _run_service(service_id):
    with services_lock:
        if not filter(lambda x: x[SERVICE_ID] == service_id, services):
            return json.dumps(ERROR_NOT_REGISTERED_SERVICE)

        m = filter(lambda x: x[SERVICE_ID] == service_id, services)[0]

        if m[SERVICE_STATUS] == STATUS_RUNNING:
            return json.dumps(ERROR_SERVICE_ALREADY_RUNNING)

        if m[SERVICE_STATUS] != STATUS_TERMINATED:
            logger.error("Wrong service status")
            exit(1)


        cmd = "\"(cd {0} && {1})\"".format(
                                        os.path.join(m[SERVICE_HOME],"ocean_don_corleone"),
                                        "./scripts/{0}_run.sh".format(m[SERVICE]))

        status, output = cautious_run_cmd_over_ssh(m[SERVICE_USER], m[SERVICE_SSH_PORT], cmd, m[SERVICE_ADDRESS])

        logger.info(("Running service ",service_id, "output", output, "status ",status))

        return json.dumps(status)

@app.route('/run_service')
def run_service():
    service_id = request.args.get('service_id')
    global services
    """ Check status of the jobs """

    return _run_service(service_id)

@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    name = request.args.get('name')
    tmp = name.split("_")
    if len(tmp) == 2:
        #Typical service_feature configuration
        if filter(lambda x: x[SERVICE_ID] == tmp[0], services):
            return json.dumps(filter(lambda x: x[SERVICE_ID] == tmp[0], services)[0].get(tmp[1], ERROR_NOT_RECOGNIZED_CONFIGURATION))
        else:
            return json.dumps(ERROR_NOT_REGISTERED_SERVICE)
    else:
        return json.dumps(ERROR_NOT_RECOGNIZED_CONFIGURATION)


@app.route('/get_services', methods=['GET'])
def get_modules():
    #return json.dumps([(m[MODULE_SERVICE_NAME], modules[MODULE_ADDRESS], m[MODULE_STATUS]) for m in modules])
    return json.dumps(services)

@app.route('/get_status', methods=['GET'])
def get_status():
    service_name = request.args.get('service_id')
    print filter(lambda x: x[SERVICE_ID] == service_name, services)
    if filter(lambda x: x[SERVICE_ID] == service_name, services):
        return filter(lambda x: x[SERVICE_ID] == service_name, services)[0][SERVICE_STATUS]
    else:
        return STATUS_NOTREGISTERED



app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    run_daemons()
    app.run(port=8881)