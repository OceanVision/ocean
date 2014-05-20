#!/usr/bin/env python
import pika
import sys

"""
Simple script pushing datasets to kafka
"""

import fnmatch
import os
import sys
from optparse import OptionParser
from nltk.tokenize import *
import logging
import codecs
# Try switching of kafka-python logger
try:
    logging.getLogger("pika").setLevel(logging.ERROR)
except:
    pass

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.append(os.path.join(os.path.dirname(__file__), '../../don_corleone/'))

from don_utils import get_configuration
import json


if __name__ == "__main__":
    credentials = pika.PlainCredentials('admin', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                'localhost', credentials=credentials))



    channel = connection.channel()

    channel.queue_declare(queue='ocean_log')


    for id in xrange(100):

        print "Sending ", id

        news = {"message":str(id), "temp_field":str(id+10)}
        message = json.dumps(news).encode("utf-8")

        channel.basic_publish(exchange='',
                            routing_key='ocean_log',
                            body=message)


        import time
        time.sleep(0.1)

    connection.close()
