/**
 * Created by staszek on 4/18/14.
 */

// See https://github.com/propensive/rapture-json-test/blob/master/src/json.scala - for scala test of json

package mantis_shrimp


import ly.stealth.testing

import org.specs2.mutable._
import java.util.UUID
import kafka.consumer._
import kafka.producer._
import kafka.utils._
import kafka.akka._
import akka.actor.{Actor, Props, ActorSystem}
import akka.routing.RoundRobinRouter

import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import scala.util.parsing.json._
import jsonParsers.scalaJson._
//import kafka.producer.{ProducerConfig, ProducerData, Producer}

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

import java.util.Properties

import kafka.api.{ FetchRequestBuilder, FetchRequest }
import kafka.javaapi.consumer.SimpleConsumer
import kafka.javaapi.FetchResponse
import kafka.javaapi.message.ByteBufferMessageSet
import scala.collection.JavaConversions._
import java.nio.ByteBuffer
import java.util.Properties
import kafka.consumer.{Consumer, ConsumerConfig}
import scala.collection.JavaConverters._

import kafka.javaapi.producer.Producer
import kafka.producer.{ KeyedMessage, ProducerConfig }

object gSandbox extends App{
   def kafkaScalaIntegrationTest(implicit parser: JsonBufferParser[String]){
       val props2: Properties = new Properties()
       props2.put("zk.connect", "ocean-db.no-ip.biz:2181")
       props2.put("metadata.broker.list", "ocean-db.no-ip.biz:771");
       props2.put("serializer.class", "kafka.serializer.StringEncoder")
       props2.put("zk.connectiontimeout.ms", "15000")

       val config: ProducerConfig = new ProducerConfig(props2)

       val producer: Producer[String, String] = new Producer[String, String](config)

       val data = new KeyedMessage[String, String]("x", "test-message, it is ok")
       producer.send(data)
       producer.close

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
     val consumer = Consumer.createJavaConsumerConnector(consumerconfig)

     val topicMap =  Map[String, Integer]("x" -> 1)

     println("about to get the comsumerMsgStreams")
     val consumerMap = consumer.createMessageStreams(topicMap.asJava)

     val streamz = consumerMap.get("x")

     val stream = streamz.iterator().next()

     println("listening... (?) ")

     val consumerIter = stream.iterator()
     while(consumerIter.hasNext()){
       System.out.println("MSG -> " + new String(consumerIter.next().message))
     }
   }

  kafkaScalaIntegrationTest
}
