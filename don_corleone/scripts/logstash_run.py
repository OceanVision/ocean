#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os

os.system("sudo -E elasticsearch stop")

ocean_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
logstash_config_path = os.path.join(ocean_root, "config/logstash.conf")

os.system("cd $LOGSTASH_HOME && sudo -E $LOGSTASH_HOME/bin/logstash -f {0} web".format(logstash_config_path))

