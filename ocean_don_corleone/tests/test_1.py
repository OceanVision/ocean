import json
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(__file__, "..")))

from run_node import install_node
from test_util import count_services

class BasicTests(unittest.TestCase):

    def test1(self):
        # Prepare config file
        os.chdir(os.path.abspath(".."))
        config = json.load(open("tests/config_test_1.json","r"))
        config["home"] = os.path.abspath(os.path.join(__file__,"../../"))
        install_node(config)
        assert(count_services(config) == 3)



if __name__ == "__main__":
    unittest.main()