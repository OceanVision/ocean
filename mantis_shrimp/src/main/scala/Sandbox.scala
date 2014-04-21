/**
 * Created by staszek on 4/18/14.
 */

// See https://github.com/propensive/rapture-json-test/blob/master/src/json.scala - for scala test of json

package mantisshrimp


import java.util.UUID
import kafka.consumer._
import kafka.producer._
import kafka.utils._

import akka.actor.{Actor, Props, ActorSystem}
import akka.routing.RoundRobinRouter

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




object Sandbox {

//
//
//   def kafkaScalaIntegrationTest(implicit parser: JsonBufferParser[String]) {
//     val props2: Properties = new Properties()
//     props2.put("zk.connect", "ocean-db.no-ip.biz:2181")
//     props2.put("metadata.broker.list", "ocean-db.no-ip.biz:771");
//     props2.put("serializer.class", "kafka.serializer.StringEncoder")
//     props2.put("zk.connectiontimeout.ms", "15000")
//
//     val config: ProducerConfig = new ProducerConfig(props2)
//
//
//
//     val producer: Producer[String, String] = new Producer[String, String](config)
//
//     val data = new KeyedMessage[String, String]("x", "test-message, it is ok5")
////     val data = new ProducerDa
//
//
//     producer.send(data)
//     producer.close
//
//
//     val consumer = new kafka.consumer.SimpleConsumer("ocean-db.no-ip.biz", 771, 100000, 64 * 1024, "tmp")
//
////     val tap = new TopicAndPartition("x", 0)
////     var requestInfo = new HashMap[TopicAndPartition, PartitionOffsetRequestInfo]()
////     requestInfo += tap -> new PartitionOffsetRequestInfo(kafka.api.OffsetRequest.EarliestTime, 1)
////     val request = new kafka.api.OffsetRequest(
////        requestInfo, kafka.api.OffsetRequest.CurrentVersion, "tmp"
////     )
////     val response = consumer.getOffsetsBefore(request)
////
//
//
//
//
//     val response = consumer.
//       fetch(new FetchRequestBuilder().addFetch("x", 0, 1, 1000).build())
//
//     println(response.hasError)
//
//     val response1 = response.messageSet("x", 0)
//
//     for (m <- response1) {
//           println(new String(m.message.payload.array()))
//     }
//
////
//     val props = new Properties()
//
//     props.put("group.id", "console-consumer-2222222")
//     props.put("socket.receive.buffer.bytes", (2 * 1024 * 1024).toString)
//     props.put("socket.timeout.ms", (ConsumerConfig.SocketTimeout).toString)
//     props.put("fetch.message.max.bytes", (1024 * 1024).toString)
//     props.put("fetch.min.bytes", (1).toString)
//     props.put("fetch.wait.max.ms", (100).toString)
//     props.put("auto.commit.enable", "true")
//     props.put("auto.commit.interval.ms", (ConsumerConfig.AutoCommitInterval).toString)
//     props.put("auto.offset.reset", "smallest")
//     props.put("zookeeper.connect", "ocean-db.no-ip.biz:2181")
//     props.put("consumer.timeout.ms", (-1).toString)
//     props.put("refresh.leader.backoff.ms", (ConsumerConfig.RefreshMetadataBackoffMs).toString)
//     val consumerconfig   = new ConsumerConfig(props)
//
//     val consumer = Consumer.createJavaConsumerConnector(consumerconfig)
//     val topicMap =  Map[String, Integer]("x" -> 1)
//
//     println("about to get the comsumerMsgStreams")
//     val consumerMap = consumer.createMessageStreams(topicMap.asJava)
//
//     val streamz = consumerMap.get("x")
//
//     val stream: KafkaStream[Array[Byte], Array[Byte]] = streamz.iterator().next()
//     val consumerIter:ConsumerIterator[Array[Byte], Array[Byte]] = stream.iterator()
//     while(consumerIter.hasNext()){
//       System.out.println("MSG -> " + new String(consumerIter.next().message))
//     }
//   }
//
//  kafkaScalaIntegrationTest
}
