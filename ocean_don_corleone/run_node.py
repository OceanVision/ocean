import os
import json
import threading
import time
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False


MASTER = "master"
LOCAL = "local"
RESPONSIBILITIES = "responsibilities"


def install_node(config):
    """ Waits for webserver to start """
    time.sleep(1)
    logger.info("Installing node")

if __name__ == "__main__":
    config = json.load(open("config.json","r"))
    logger.info(("Configuration file ", config))

    t = threading.Thread(target=install_node, args=(config,))
    t.start()

    if config[MASTER]:
        if config[MASTER] == LOCAL:
            os.system("python ocean_don_corleone.py")
        else:
            os.system("gunicorn -c gunicorn_config.py ocean_don_corleone:app")

