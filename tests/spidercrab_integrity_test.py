#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Testing of availability and communication of dependent system elements
    NOTE: Does not harm graph database.
"""
import sys, os
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../lionfish/"))
import python_lionfish
from python_lionfish.client.client import Client

from don_corleone import don_utils as du


def check_corleone_config():
    """
        Returns true if don_corleone config is provided
    """
    try:
#       Checking for neo4j is obsolete because there won't be such service
#       Lionfish is taking over neo4j (no REST console)
#        neo4j_host = du.get_configuration('neo4j', 'host')
#        neo4j_port = du.get_configuration('neo4j', 'port')
        lionfish_host = du.get_configuration('lionfish', 'host')
        lionfish_port = du.get_configuration('lionfish', 'port')
    except Exception as error:
        print unicode(error)
        return False
#   Again: obsolete
#    if not neo4j_host or not neo4j_port or not lionfish_host \
#            or not lionfish_port:

    if not lionfish_port or not lionfish_host:
        return False
    return True


def check_lionfish_communication():
    """
        Returns true if lionfish works OK
    """
    lionfish_host = du.get_configuration('lionfish', 'host')
    lionfish_port = du.get_configuration('lionfish', 'port')

    lionfish_client = Client(lionfish_host, lionfish_port)
    lionfish_client.connect()
    lionfish_client.create_model_node('spidercrab_integrity_test')
    found_instances = lionfish_client.get_model_nodes()
    model_instance = None
    model_uuid = ''
    for model in found_instances:
        if model['model_name'] == 'spidercrab_integrity_test':
            model_uuid = model['uuid']
            model_instance = model
    assert(model_instance == lionfish_client.get_by_uuid(model_uuid))
    lionfish_client.delete_node(model_uuid)
    return True


def warn_that_not_local(service, value):
    print 'You are not using a local ' + str(service) + ' (' \
          + str(value) + ') - is it intended?'


def warn_if_not_local():
    # See comment in check_corleone_config()
    #neo4j_location = str(du.get_configuration('neo4j', 'host'))
    #if neo4j_location != 'localhost' and neo4j_location != '127.0.0.1':
    #    warn_that_not_local('Neo4j', neo4j_location)

    lionfish_location = str(du.get_configuration('lionfish', 'host'))
    if lionfish_location != 'localhost' and lionfish_location != '127.0.0.1':
        warn_that_not_local('Lionfish', lionfish_location)


if __name__ == '__main__':
    print '\nTesting system availability...'
    assert(du.get_ocean_root_dir())
    assert(check_corleone_config())
    warn_if_not_local()

    print '\nChecking communication...'
    assert(check_lionfish_communication())
    print 'PASSED'
