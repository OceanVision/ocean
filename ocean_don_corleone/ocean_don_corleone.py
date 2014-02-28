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


ERROR_NOT_RUNNING_SERVICE = "not_running_service_error"
ERROR_ALREADY_EXISTING_SERVICE = "already_existing_service"
ERROR_NOT_REGISTERED_SERVICE = "not_registered_service_error"
ERROR_NOT_RECOGNIZED_CONFIGURATION = "not_recognized_configuration"
ERROR_NOT_REACHABLE_SERVICE = "not_reachable_service"
ERROR_FAILED_SERVICE_RUN = "failed_service_run"
OK = "ok"

SERVICE_ODM = "odm"
SERVICE_NEO4J = "neo4j"
SERVICE_NEWS_FETCHER_MASTER = "news_fetcher_master"


SERVICE = "service"
SERVICE_NAME = "name"
SERVICE_STATUS = "status"
SERVICE_ADDRESS = "address"
SERVICE_PORT = "port"
SERVICE_HOME = "home"
SERVICE_RUN_CMD = "run_cmd"

COMMAND_DEFAULT = "default"

STATUS_NOTREGISTERED = "not_registered"
STATUS_TERMINATED = "terminated"
STATUS_RUNNING = "running"



services = []


service_tmp = {"service":"odm",
               "name":"odm", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":2231,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: COMMAND_DEFAULT
               }
service_tmp2 = {"service":"neo4j",
               "name":"neo4j", "status":STATUS_TERMINATED, "address":"ocean-db.no-ip.biz", "port":2231,
               "home":"/home/ocean/public_html/ocean", SERVICE_RUN_CMD: COMMAND_DEFAULT
               }

services.append(service_tmp)
services.append(service_tmp2)

### Setup service check commands ###
service_check_commands = {}
service_check_commands[SERVICE_ODM] = "ps ax|grep odm_server.py$"
service_check_commands[SERVICE_NEO4J] = """echo `ps ax | grep neo4j | wc -l`"""

#(( `ps ax | grep neo4j | wc -l` > 1 ))

service_run_commands = {}
service_run_commands[SERVICE_ODM] = "python odm_server.py &"
service_run_commands[SERVICE_NEO4J] = "echo {sudo_pass} | sudo -S service neo4j-service start"
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



def status_checker_job():
    global services
    """ Check status of the jobs """
    logger.info("Running status checking daemon")
    while True:
        time.sleep(10)
        for id, m in enumerate(services):
            prog = subprocess.Popen(["ssh ocean@{0} -p{1} ls".
                                     format(m[SERVICE_ADDRESS],m[SERVICE_PORT])], stdout=subprocess.PIPE, shell=True)
            prog.communicate()

            logger.info(("Checking ssh (reachability) for ",m[SERVICE_NAME], "result ", prog.returncode))

            if prog.returncode != 0:
                services.remove(id)
                logger.info("Service not reachable")
                continue

            prog = subprocess.Popen(["ssh ocean@{0} -p{1} \"cd {2} && ({3})\"".
                                     format(m[SERVICE_ADDRESS],
                                            m[SERVICE_PORT],
                                            m[SERVICE_HOME],

                                            service_check_commands[m[SERVICE]].format(sudo_pass=open("ocean_password","r").read())


                                    )
                                    ],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output = prog.communicate()[1]

            logger.info(("Checking server availability for ",m[SERVICE_NAME], "result ", prog.returncode))

            logger.info(output)

            if prog.returncode != 0:
                logger.error("Service terminated")
                logger.error(output)
                m[SERVICE_STATUS] = STATUS_TERMINATED
                continue

            m[SERVICE_STATUS] = STATUS_RUNNING


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


@app.route('/run_service')
def run_service():
    service_name = request.args.get('service_name')
    global services
    """ Check status of the jobs """

    if not filter(lambda x: x[SERVICE_NAME] == service_name, services):
        return ERROR_NOT_REGISTERED_SERVICE

    m = filter(lambda x: x[SERVICE_NAME] == service_name, services)[0]


    prog = subprocess.Popen(["ssh ocean@{0} -p{1} ls".
                             format(m[SERVICE_ADDRESS],m[SERVICE_PORT])], stdout=subprocess.PIPE, shell=True)
    prog.communicate()

    logger.info(("Checking ssh (reachability) for ",m[SERVICE_NAME], "result ", prog.returncode))

    if prog.returncode != 0:
        return json.dumps(ERROR_NOT_REACHABLE_SERVICE)

    prog = subprocess.Popen(["ssh ocean@{0} -p{1} \"cd {2} && ({3})\"".
                             format(m[SERVICE_ADDRESS],
                                    m[SERVICE_PORT],
                                    m[SERVICE_HOME],


                                    service_check_commands[m[SERVICE]].format(sudo_pass=open("ocean_password","r").read())
                                    if m[SERVICE_RUN_CMD] == COMMAND_DEFAULT
                                    else m[SERVICE_RUN_CMD].format(sudo_pass=open("ocean_password","r").read())

                            )
                            ],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = prog.communicate()[1]

    logger.info(("Running service ",m[SERVICE_NAME], "result ", prog.returncode))

    logger.info(output)

    if prog.returncode != 0:
        return json.dumps(ERROR_FAILED_SERVICE_RUN)

    m[SERVICE_STATUS] = STATUS_RUNNING

    return json.dumps(OK)


@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    name = request.args.get('name')
    return "Hello world!"
    tmp = name.split("_")
    if len(tmp) == 2:
        #Typical service_feature configuration
        if filter(lambda x: x[SERVICE_NAME] == tmp[0], services):
            return json.dumps(filter(lambda x: x[SERVICE_NAME] == tmp[0], services)[0][tmp[1]])
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
    service_name = request.args.get('service_name')
    print filter(lambda x: x[SERVICE_NAME] == service_name, services)
    if filter(lambda x: x[SERVICE_NAME] == service_name, services):
        return filter(lambda x: x[SERVICE_NAME] == service_name, services)[0][SERVICE_STATUS]
    else:
        return STATUS_NOTREGISTERED



app.wsgi_app = ProxyFix(app.wsgi_app)




if __name__ == '__main__':
    run_daemons()
    app.run(port=8881)