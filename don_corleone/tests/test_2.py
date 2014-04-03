import json
import os
import sys
import unittest

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from run_node import install_node, run_node
from don_utils import get_configuration
from test_util import count_services

class MediumTests(unittest.TestCase):

    def test1(self):
        """ Test configuration with local neo4j """

        os.chdir(os.path.abspath(".."))

        # Prepare config filu
        config = json.load(open(os.path.join(os.path.dirname(__file__),\
            "tests/config_test_2_a.json"),"r"))
        config["home"] = os.path.abspath(os.path.join(__file__,"../../"))
        run_node(config)

        config = json.load(open(os.path.join(os.path.dirname(__file__),\
            "tests/config_test_2_b.json"),"r"))
        config_b = config
        config["home"] = os.path.abspath(os.path.join(__file__,"../../"))
        run_node(config)

        assert(count_services(config) == 3) # Services count = 3
        assert(get_configuration("neo4j","port", config_b) == 7476) # Local neo4j port

        print "Terminating don corleone node"
        os.system("scripts/don_corleone_terminate.sh")



if __name__ == "__main__":
    unittest.main()
