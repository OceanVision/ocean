import os
import json
import threading
import time
import logging
import urllib2, urllib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


MASTER = "master"
LOCAL = "127.0.0.1:8881"
RESPONSIBILITIES = "node_responsibilities"


def install_node(config):
    """ Waits for webserver to start """
    time.sleep(1)
    logger.info("Installing the node")
    print config[RESPONSIBILITIES]



    for id, responsibility in enumerate(config[RESPONSIBILITIES]):
        logger.info("Registering "+str(id)+" responsibility "+str(responsibility))



        service, service_id = responsibility[0].split(":") if (len(responsibility[0].split(":"))>1)\
            else (responsibility[0], responsibility[0])

        additional_config = responsibility[1]


        params = urllib.urlencode\
                ({"service":service, "service_id":service_id, "config":json.dumps(config),
                  "additional_config":json.dumps(additional_config)
                  })


        response = urllib2.urlopen(config[MASTER]+"/register_service", params).read()
        print response


if __name__ == "__main__":
    config = json.load(open("config.json","r"))

    logger.info(("Configuration file ", config))


    t = threading.Thread(target=install_node, args=(config,))
    t.start()

    if config[MASTER]:
        if config[MASTER] == LOCAL:
            if os.system("./scripts/don_corleone_test.sh") != 0:
                logger.info("Running DonCorleone on local setting")
                os.system("python ocean_don_corleone.py")
        else:
            #TODO: correct condition??
            if os.system("./scripts/don_corleone_test.sh") != 0:
                logger.info("Running DonCorleone on master setting")
                os.system("workon ocean && gunicorn -c gunicorn_config.py ocean_don_corleone:app")

