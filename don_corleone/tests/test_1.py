import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_node import run_node
from don_utils import get_configuration
from test_util import count_services, get_test_config

class BasicTests(unittest.TestCase):

    def test1(self):
        """ Simple test - testing configuration with 3 responsibilities """

        os.chdir(os.path.abspath(".."))

        # Prepare config file
        config = get_test_config("config_test_1.json")
        run_node(config, hang=False)

        assert(count_services(config) == 3)
        print "Terminating don corleone node"
        # Terminate
        os.system("scripts/don_corleone_terminate.sh")
        # Check if terminated correctly
        assert(os.system("scripts/don_corleone_test.sh") != 0)

if __name__ == "__main__":
    unittest.main()
