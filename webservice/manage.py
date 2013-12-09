#!/usr/bin/env python
import os
import sys
from signal import *

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../graph_workers"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../graph_views"))

#

#
#
from ocean_master import OC, OceanMaster
#


def clean(*args):
    global gwm
    print "Terminating OceanMaster..."
    OC.terminate()
    os.remove('REMOVE_ME_BEFORE_RUNSERVER')
    exit(0)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocean.settings")

    for sig in (SIGINT,):
        signal(sig, clean)

    from django.core.management import execute_from_command_line

    if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
        #TODO: that's just a giagiantic (:p) workaround, see github issue
        if not os.path.isfile('REMOVE_ME_BEFORE_RUNSERVER'):
            open('REMOVE_ME_BEFORE_RUNSERVER','w').write('first time')
            os.system("ps | grep python")
            OC = OceanMaster()
            OC.run()

    execute_from_command_line(sys.argv)
