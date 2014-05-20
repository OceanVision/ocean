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


#

don_dir = os.path.abspath(os.path.join(__file__, "../../.."))
don_data_dir = os.path.join(don_dir, "data")

def document_to_word_list(text):
    """ Return concatenated list of bare words """
    text_sent = sent_tokenize(text)
    words = [word_tokenize(sentence) for sentence in text_sent]
    all_words = []
    for words_subset in words: all_words += words_subset #flattening
    return all_words

def get_documents(root_dir=os.path.join(don_data_dir, "Reuters115"), encoding="iso-8859-1"):
    """ Reads all files in given directory"""
    print don_data_dir
    matches = []
    documents = []
    for root, dirnames, filenames in os.walk(root_dir):
      for id, filename in enumerate(filenames):
          print "Reading id ",id, " filename ",filename
          documents.append(open(root+"/"+filename,"r").read().decode(encoding))
    return documents

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option(
        '-r',
        '--root_dir',
        dest='root_dir',
        default=os.path.join(don_data_dir, "Reuters115"),
        help='Data directory'
    )
    parser.add_option(
        '-n',
        '--name',
        dest='name',
        default='mock_dataset_1',
        help='Dataset name'
    )
    parser.add_option(
        '-e',
        '--file_encoding',
        dest='file_encoding',
        default="iso-8859-1",
        help='File encoding - check by unix command file'
    )
    (options, args) = parser.parse_args()

    print "Connecting to ","{0}:{1}".format(get_configuration("kafka","host"),get_configuration("kafka","port"))

    credentials = pika.PlainCredentials('admin', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                'localhost', credentials=credentials))



    channel = connection.channel()

    channel.queue_declare(queue='mantis_totag')


    for id, d in enumerate(get_documents(options.root_dir, options.file_encoding)):

        print "Sending ", id

        words = document_to_word_list(d)
        news = {"uuid":str(id), "title":(u" ".join(words[0:10])).encode("utf-8"), "summary":d.encode("utf8"), "text":""}
        message = json.dumps(news).encode("utf-8")

        channel.basic_publish(exchange='',
                            routing_key='mantis_totag',
                            body=message)


    connection.close()
