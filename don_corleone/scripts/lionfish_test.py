#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../lionfish/")))
sys.path.append(os.path.abspath(os.path.join(__file__, "..")))
sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))

import python_lionfish
from python_lionfish.client.client import Client
from don_corleone import don_utils as du

def check_lionfish_communication():
    """
        Returns true if lionfish works OK
    """
    lionfish_host = du.get_configuration('lionfish', 'host')
    lionfish_port = du.get_configuration('lionfish', 'port')
    print "Connecting to ", lionfish_host, lionfish_port
    lionfish_client = Client(lionfish_host, lionfish_port)
    lionfish_client.connect()
    found_instances = lionfish_client.get_by_uuid("xwdjwdwjw")
    lionfish_client.disconnect()
    return True



if check_lionfish_communication():
    print "Lionfish running"
    exit(0)
else:
    exit(1)
