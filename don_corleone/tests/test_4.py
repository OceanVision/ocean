import urllib2
import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_node import install_node, run_node
from don_utils import get_configuration, run_procedure, get_don_corleone_url
from test_util import count_services, get_test_config

class BasicTests(unittest.TestCase):

    def test4(self):
        """ Simple test - testing configuration with 2 responsibilities with custom service_id """

        os.chdir(os.path.abspath(".."))

        # Prepare config file
        config = get_test_config("config_test_4.json")

        

        run_node(config, hang=False)

        print run_procedure(config, "get_services")

        response = json.loads(urllib2.urlopen(get_don_corleone_url(config)
                               +"/get_configuration?service_id=moj_neo4j&node_id=staszek&config_name=port").read())


        print response
        assert(response['result']==7474)
        print count_services(config)
        assert(count_services(config) == 2)
        print "Terminating don corleone node"
        # Terminate
        os.system("scripts/don_corleone_terminate.sh")
        # Check if terminated correctly
        assert(os.system("scripts/don_corleone_test.sh") != 0)

if __name__ == "__main__":
    unittest.main()
