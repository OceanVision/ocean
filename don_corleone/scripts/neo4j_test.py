#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys, os


sys.path.append(os.path.abspath(os.path.join(__file__, "../../..")))

from don_corleone import don_utils as du
neo4j_host = du.get_configuration('neo4j', 'host')
neo4j_port = du.get_configuration('neo4j', 'port')


try:
    import socket
    sock = socket.socket()
    sock.connect((neo4j_host, neo4j_port))

    print "Neo4j running"

    sock.close()
except:
    print "Neo4j is not running"
    exit(1)

