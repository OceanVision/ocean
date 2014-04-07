import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_node import install_node, run_node
from don_utils import get_configuration, run_procedure
from test_util import count_services, get_test_config

class BasicTests(unittest.TestCase):

    def test3(self):
        """ Simple test - testing configuration with 3 responsibilities and reversed ssh"""

        os.chdir(os.path.abspath(".."))

        # Prepare config file
        config = get_test_config("config_test_3.json")
        run_node(config, hang=False)
        print run_procedure(config, "get_services")
        print count_services(config)
        assert(count_services(config) == 2)
        print "Terminating don corleone node"
        # Terminate
        os.system("scripts/don_corleone_terminate.sh")
        # Check if terminated correctly
        assert(os.system("scripts/don_corleone_test.sh") != 0)

if __name__ == "__main__":
    unittest.main()
