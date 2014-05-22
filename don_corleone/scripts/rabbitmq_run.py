#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os

parser = OptionParser()
parser.add_option(
    '-p',
    '--port',
    dest='port',
    default=5672,
    help='On which port start rabbitmq'
)
(options, args) = parser.parse_args()

os.system("sudo -E RABBITMQ_NODE_PORT={0} rabbitmq-server".format(options.port))
