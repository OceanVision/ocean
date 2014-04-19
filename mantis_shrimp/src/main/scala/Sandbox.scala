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

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

object Sandbox extends App with Logging {
   def kafkaScalaIntegrationTest(implicit parser: JsonBufferParser[String]){

     info("Fetching kafka configs")
     info(DonCorleoneUtils.get_configuration[Int]("kafka","port").toString())
     info(DonCorleoneUtils.get_configuration[String]("kafka","host").toString())

     val kafka_port = DonCorleoneUtils.get_configuration[Int]("kafka","port")
     val kafka_host = DonCorleoneUtils.get_configuration[String]("kafka","host")

     val testMessage = UUID.randomUUID().toString
     val testTopic = UUID.randomUUID().toString
     val groupId_1 = UUID.randomUUID().toString

     var testStatus = false

     info("starting sample broker testing")
     val producer = new KafkaProducer(testTopic,f"$kafka_host%s:$kafka_port%d")
     producer.send(testMessage)

     val consumer = new KafkaConsumer(testTopic,groupId_1,f"$kafka_host%s:$kafka_port%d")

     def exec(binaryObject: Array[Byte]) = {
       val message = new String(binaryObject)
       info("testMessage = " + testMessage + " and consumed message = " + message)
       consumer.close()
       testStatus = true
     }

     val json_example = json""" {"ala":13, "beka":[1,2,"ala2"]} """

     println(json_example) ;

     println(json_example.ala.as[Int]);
   }

  kafkaScalaIntegrationTest
}
