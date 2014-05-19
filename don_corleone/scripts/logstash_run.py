#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os

os.system("sudo -E elasticsearch start")

ocean_root = os.path.join(__file__, "../../")
logstash_config_path = os.path.join(ocean_root, "config/logstash.conf")

os.system("sudo -E logstash -f {0} web".format(logstash_config_path))

