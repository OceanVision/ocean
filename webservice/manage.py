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
import ocean_master
#


def clean(*args):
    print "Terminating OceanMaster..."
    ocean_master.OC.terminate()
    os.remove('REMOVE_ME_BEFORE_RUNSERVER')
    exit(0)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocean.settings")

    for sig in (SIGINT,):
        signal(sig, clean)

    from django.core.management import execute_from_command_line

    if len(sys.argv) >= 2 and sys.argv[1] == "runserver":
        #TODO: that's just a giagiantic (:p) workaround, see github issue
        if os.path.isfile('REMOVE_ME_BEFORE_RUNSERVER'):
            ocean_master.OC = ocean_master.OceanMaster()
            ocean_master.OC.run()
            import ocean_master
            print ocean_master.OC
        if not os.path.isfile('REMOVE_ME_BEFORE_RUNSERVER'):
            open('REMOVE_ME_BEFORE_RUNSERVER','w').write('first time')


    execute_from_command_line(sys.argv)
