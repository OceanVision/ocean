"""
Mock dataset for mantis testing
"""


from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from kafka.producer import SimpleProducer, KeyedProducer

from py2neo import neo4j
import uuid
import os
import socket
import logging
from threading import Thread
import sys
import json
import logging
import optparse



logging.getLogger("kafka").setLevel(logging.ERROR)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../don_corleone/'))

from don_utils import get_configuration


if __name__ == "__main__":

    parser = optparse.OptionParser()

    parser.add_option(
        '-n',
        '--name',
        dest='name',
        default='mantis_mock_dataset_1',
        help='Topic name'
    )

    (options, args) = parser.parse_args()

    print get_configuration("kafka", "port")
    print get_configuration("kafka", "host")

    kafka = KafkaClient("{0}:{1}".format(get_configuration("kafka","host"),get_configuration("kafka","port")))

    # To consume messages
    consumer = SimpleConsumer(kafka, "mantis", options.name)

    consumer.seek(-1, 2)

    for message in consumer:
        print(message)

    kafka.close()
