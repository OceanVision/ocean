""" Temporary file - testing odm, we can rewrite
    it later to unit tests or something like this
"""


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

sys.path.append(os.path.join(os.path.dirname(__file__), "../graph_workers"))

from odm_server import DatabaseManager
from odm_client import ODMClient

if __name__ == "__main__":
    db = DatabaseManager()
    print db.get_all_instances(model_name="ContentSource")
    

    print db.get_by_uuid(node_uuid="x")
    
    cl = ODMClient()
    cl.connect()
    print cl.get_all_instances(model_name="ContentSource")
