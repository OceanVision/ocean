import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_node import install_node, run_node
from don_utils import get_configuration
from test_util import count_services

class BasicTests(unittest.TestCase):

    def test1(self):
        """ Simple test - testing configuration with 3 responsibilities """

        os.chdir(os.path.abspath(".."))

        # Prepare config file
        config = json.load(open(os.path.join(os.path.dirname(__file__),"tests/config_test_1.json"),"r"))
        config["home"] = os.path.abspath(os.path.join(__file__,"../../"))
        run_node(config)
        assert(count_services(config) == 3)
        print "Terminating don corleone node"
        os.system("scripts/don_corleone_terminate.sh")

if __name__ == "__main__":
    unittest.main()
