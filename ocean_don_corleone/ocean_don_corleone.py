""" Server responsible for managing Ocean state.
Ocean admin should be run on every node of our Ocean cluster.
"""

import json
import threading
import logging
import os
import paramiko
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


ERROR_NOT_RUNNING_SERVICE = "not_running_service_error"



SERVICE_ODM = "odm"
SERVICE_NEO4j = "neo4j"


SERVICE = "service"
SERVICE_NAME = "name"
SERVICE_STATUS = "status"
SERVICE_ADDRESS = "address"
SERVICE_PORT = "port"
SERVICE_HOME = "home"


STATUS_NOTREGISTERED = "not_registered"
STATUS_TERMINATED = "terminated"
STATUS_RUNNING = "running"



services = []


service_tmp = {"service":"odm",
               "name":"odm", "status":"", "address":"ocean-db.no-ip.biz", "port":2231,
               "home":"/home/ocean/public_html/ocean"
               }
services.append(service_tmp)

### Setup service check commands ###
service_check_commands = {}
service_check_commands[SERVICE_ODM] = "ps ax|grep odm_server.py$"

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
    global modules
    """ Check status of the jobs """
    logger.info("Running status checking daemon")
    while True:
        time.sleep(1)
        for id, m in enumerate(services):
            prog = subprocess.Popen(["ssh ocean@{0} -p{1} ls".
                                     format(m[SERVICE_ADDRESS],m[SERVICE_PORT])], stdout=subprocess.PIPE, shell=True)
            prog.communicate()

            logger.info(("Checking ssh (reachability) for ",m[SERVICE_NAME], "result ", prog.returncode))

            if prog.returncode != 0:
                services.remove(id)
                logger.info("Service not reachable")
                continue

            prog = subprocess.Popen(["ssh ocean@{0} -p{1} cd {2} && {3}".
                                     format(m[SERVICE_ADDRESS],m[SERVICE_PORT],
                                     m[SERVICE_HOME], service_check_commands[m[SERVICE]])
                                     ],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output = prog.communicate()[1]

            logger.info(("Checking server availability for ",m[SERVICE_NAME], "result ", prog.returncode))


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

@app.route('/get_configuration', methods=["GET"])
def get_configuraiton():
    name = request.args.get('name')
    return "Hello world!"

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