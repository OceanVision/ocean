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

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))
sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../graph_workers/graph_workers'))

from don_utils import get_configuration



kafka = KafkaClient("{0}:{1}".format(get_configuration("kafka","host"),get_configuration("kafka","port"))


producer = SimpleProducer(kafka, batch_send=True,
                          batch_send_every_n=20,
                          batch_send_every_t=60)


# To send messages synchronously
producer = SimpleProducer(kafka)
producer.send_messages("my-topic3", "some message")
producer.send_messages("my-topic3", "this method", "is variadic")


# To wait for acknowledgements
# ACK_AFTER_LOCAL_WRITE : server will wait till the data is written to
#                         a local log before sending response
# ACK_AFTER_CLUSTER_COMMIT : server will block until the message is committed
#                            by all in sync replicas before sending a response
producer = SimpleProducer(kafka, async=False,
                          req_acks=SimpleProducer.ACK_AFTER_LOCAL_WRITE,
                          ack_timeout=2000)
response = producer.send_messages("my-topic3", "async message")

if response:
    print(response[0].error)
    print(response[0].offset)

# To send messages in batch. You can use any of the available
# producers for doing this. The following producer will collect
# messages in batch and send them to Kafka after 20 messages are
# collected or every 60 seconds
# Notes:
# * If the producer dies before the messages are sent, there will be losses
# * Call producer.stop() to send the messages and cleanup
producer = SimpleProducer(kafka, batch_send=True,
                          batch_send_every_n=20,
                          batch_send_every_t=60)

# To consume messages
consumer = SimpleConsumer(kafka, "my-group2", "my-topic3")
for message in consumer:
    print(message)

kafka.close()
