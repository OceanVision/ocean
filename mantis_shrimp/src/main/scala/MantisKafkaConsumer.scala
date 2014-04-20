/**
 * Created by staszek on 4/20/14.
 */


import ly.stealth.testing

import org.specs2.mutable._
import java.util.UUID
import kafka.consumer._
import kafka.producer._
import kafka.utils._
import kafka.akka._
import akka.actor.{Actor, Props, ActorSystem}
import akka.routing.RoundRobinRouter

import monifu.concurrent.atomic._

import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import scala.util.parsing.json._
import jsonParsers.scalaJson._
import kafka.common.TopicAndPartition
import scala.collection.immutable.HashMap

//import kafka.producer.{ProducerConfig, ProducerData, Producer}

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

import java.util.Properties

import kafka.api.{OffsetRequest, PartitionOffsetRequestInfo, FetchRequestBuilder, FetchRequest}
import kafka.javaapi.consumer.SimpleConsumer
import kafka.javaapi.FetchResponse
import kafka.javaapi.message.ByteBufferMessageSet
import scala.collection.JavaConversions._
import java.nio.ByteBuffer
import java.util.Properties
import kafka.consumer.{Consumer, ConsumerConfig}

import kafka.serializer.StringDecoder

import scala.collection.JavaConverters._

import kafka.javaapi.producer.Producer
import kafka.producer.{ KeyedMessage, ProducerConfig }



/*
*
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements. See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership. The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License. You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied. See the License for the
* specific language governing permissions and limitations
* under the License.
*
*/


import kafka.common.{ OffsetOutOfRangeException, ErrorMapping }
import kafka.api._
import kafka.common.TopicAndPartition
import kafka.api.PartitionOffsetRequestInfo
import kafka.message.MessageAndOffset


import kafka.consumer.SimpleConsumer
import kafka.api._
import kafka.common.TopicAndPartition
import kafka.consumer.ConsumerConfig

import kafka.common.ErrorMapping
import kafka.api._
import kafka.api.PartitionOffsetRequestInfo
import kafka.message.MessageAndOffset


import org.specs2.mutable._
import java.util.UUID
import kafka.consumer._
import kafka.utils._
import kafka.akka._
import akka.actor.{Actor, ActorSystem}

import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import jsonParsers.scalaJson._
import scala.collection.immutable.HashMap
import scala.collection.mutable

//import kafka.producer.{ProducerConfig, ProducerData, Producer}

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

import java.util.Properties

import kafka.api.FetchRequest
import kafka.javaapi.message.ByteBufferMessageSet
import java.nio.ByteBuffer
import java.util.Properties
import kafka.consumer.Consumer


import scala.collection.JavaConverters._

import kafka.producer.KeyedMessage

import kafka.api._


import kafka.common.{ OffsetOutOfRangeException, ErrorMapping }
import kafka.api.PartitionOffsetRequestInfo


import kafka.consumer.SimpleConsumer
import kafka.consumer.ConsumerConfig
import java.nio.file.{Paths, Files}

import akka.actor.{Actor, Props, ActorSystem}

/**
 * Basic Kafka Actor. Note that it will be sufficient in most cases because
 * We will create new topics for new big chunks of news. I do not want
 * to focus on implementing this one single actor.
 */
class MantisKafkaFetcherBasic extends Actor {
    //Main source of news
    val topic = "mantis_mock_dataset_2"
    //Stop fetching thread when exceedes
    val maximumQueueSize = 1000
    //Queue to store messages
    val Q = new mutable.SynchronizedQueue[String]()

    // Prepare Kafka High Level Consumer
    val props = new Properties()
    props.put("group.id", "console-consumer-2222222")
    props.put("socket.receive.buffer.bytes", (2 * 1024 * 1024).toString)
    props.put("socket.timeout.ms", (ConsumerConfig.SocketTimeout).toString)
    props.put("fetch.message.max.bytes", (1024 * 1024).toString)
    props.put("fetch.min.bytes", (1).toString)
    props.put("fetch.wait.max.ms", (100).toString)
    props.put("auto.commit.enable", "true")
    props.put("auto.commit.interval.ms", (ConsumerConfig.AutoCommitInterval).toString)
    props.put("auto.offset.reset", "smallest")
    props.put("zookeeper.connect", "ocean-db.no-ip.biz:2181")
    props.put("consumer.timeout.ms", (-1).toString)
    props.put("refresh.leader.backoff.ms", (ConsumerConfig.RefreshMetadataBackoffMs).toString)
    val consumerconfig   = new ConsumerConfig(props)
    val consumer = kafka.consumer.Consumer.createJavaConsgumerConnector(consumerconfig)
    val topicMap =  Map[String, Integer]("mantis_mock_dataset_2" -> 1)
    val consumerMap = consumer.createMessageStreams(topicMap.asJava)
    val streamz = consumerMap.get("mantis_mock_dataset_2")
    val stream: KafkaStream[Array[Byte], Array[Byte]] = streamz.iterator().next()
    val consumerIter:ConsumerIterator[Array[Byte], Array[Byte]] = stream.iterator()

    // Fetch already tagged news (note this will be synchronized through offsets
    // the more advanced version
    tagged =  if(Files.exists("fetched"))

    val fetcher_thread = new Thread(new Runnable {
        while(consumerIter.hasNext()){


          System.out.println("MSG -> " + new String(consumerIter.next().message))
        }

    })



  def receive = {
    case "hello" => println("hello back at you")
    case _       => println("huh?")
  }
}

object Main {
  def main(a: Array[String]) {

    val system = ActorSystem("HelloSystem")
    // default Actor constructor
    val helloActor = system.actorOf(Props[HelloActor], name = "helloactor")
    helloActor ! "hello"
    helloActor ! "buenos dias2"
  }
}