import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_node import run_node
from don_utils import get_configuration, run_procedure
from test_util import count_services, get_test_config
from terminate_node import terminate_node

class BasicTests(unittest.TestCase):

    def test5(self):
        """ Simple test - testing configuration with lionfish scala if is adding"""

        os.chdir(os.path.abspath(".."))

        # Prepare config file
        self.config = get_test_config("config_test_5.json")
        config = self.config
        run_node(config, hang=False)
        print run_procedure(config, "get_services")
        print count_services(config)

        raw_input("Press [enter] to finish test")

        assert(count_services(config, running=True) == 3)

        config = self.config
        print "Terminating don corleone noode"
        terminate_node(config)
        # Terminate
        os.system("scripts/don_corleone_terminate.sh")
        # Check if terminated correctly
        assert(os.system("scripts/don_corleone_test.sh") != 0)

if __name__ == "__main__":
    unittest.main()
