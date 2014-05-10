import json
import os
import sys
import unittest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Don Corleone imports
from run_node import run_node
from don_utils import get_configuration, run_procedure
from test_util import count_services, get_test_config

class MediumTests(unittest.TestCase):

    def test1(self):
        """ Test configuration with local neo4j """

        os.chdir(os.path.abspath(".."))

        # Prepare config filu
        config = get_test_config("config_test_2_a.json")
        run_node(config, hang=False)

        config = get_test_config("config_test_2_b.json")
        config_b = config
        run_node(config, hang=False)

        print count_services(config) 
        print run_procedure(config, "get_services")

        assert(count_services(config) == 3) # Services count = 3
        assert(get_configuration("neo4j","port", config_b) == 7476) # Local neo4j port

        print "Terminating don corleone node"
        os.system("scripts/don_corleone_terminate.sh")



if __name__ == "__main__":
    unittest.main()
