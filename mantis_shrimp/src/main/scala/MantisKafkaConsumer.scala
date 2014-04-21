/**
 * Created by staszek on 4/20/14.
 */

import akka.actor.{Actor, Props, ActorSystem}

import java.util.Properties

import kafka.api.{OffsetRequest, PartitionOffsetRequestInfo, FetchRequestBuilder, FetchRequest}
import kafka.consumer.{Consumer, ConsumerConfig}
import kafka.producer.{ KeyedMessage, ProducerConfig }

import kafka.common.{ OffsetOutOfRangeException, ErrorMapping }

import rapture.io._
import rapture.json._
import jsonParsers.scalaJson._


import java.util.UUID
import kafka.consumer._
import kafka.utils._
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

import scala.collection.JavaConverters._
import kafka.common.{ OffsetOutOfRangeException, ErrorMapping }
import kafka.consumer.ConsumerConfig
import java.nio.file.{Paths, Files}

import akka.actor.{Actor, Props, ActorSystem}

import java.io.FileWriter
import java.lang.{Runnable, Thread}
/**
 * Basic Kafka Actor. Note that it will be sufficient in most cases because
 * We will create new topics for new big chunks of news. I do not want
 * to focus on implementing this one single actor.
 */
class MantisKafkaFetcherBasic(topic: String = "mantis_mock_dataset_2") extends Actor {
    //Encoding for JSON parsing
    implicit val enc = Encodings.`UTF-8`
    //Stop fetching thread when exceedes
    val maximumQueueSize =  1000
    //Queue to store messages
    val Q = new mutable.SynchronizedQueue[Map[String, AnyRef]]()

    // Prepare Kafka High Level Consumer. TODO: Create own wrapper around this
    val props = new Properties()
    props.put("group.id", topic+"_consumer")
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
    val consumer = kafka.consumer.Consumer.createJavaConsumerConnector(consumerconfig)
    val topicMap =  Map[String, Integer]("mantis_mock_dataset_2" -> 1)
    val consumerMap = consumer.createMessageStreams(topicMap.asJava)
    val streamz = consumerMap.get("mantis_mock_dataset_2")
    val stream: KafkaStream[Array[Byte], Array[Byte]] = streamz.iterator().next()
    val consumerIter:ConsumerIterator[Array[Byte], Array[Byte]] = stream.iterator()

    // Fetch already tagged news (note this will be synchronized through offsets
    // the more advanced version.
    val tagged_in_current_topic_list =  if(Files.exists(Paths.get("tagged.dat")))
          scala.io.Source.fromFile("tagged.dat").mkString.split("\\r?\\n").toList else
          List()
    var tagged_in_current_topic = scala.collection.mutable.Set[String]()
    tagged_in_current_topic ++= tagged_in_current_topic

  /**
   * Commits already tagged to file. Not implemented correctly now (should update list)
   */
    private def commitTagged()={
         val fw = new java.io.FileWriter("tagged.dat")
         try fw.write(tagged_in_current_topic_list.mkString("/n"))
         finally fw.close()
    }

    // Fetching thread running in background
    val fetcher_thread = new java.lang.Thread(new java.lang.Runnable {
      def run(){
        while(consumerIter.hasNext()){
          val msgoffset = consumerIter.next()
          // Try parsing - if format is incorrect write error
          try {
            val msg = JsonBuffer.parse(new String(msgoffset.message))
            val uuid = msg.uuid.as[String]
            if (!tagged_in_current_topic.contains(uuid)) {
              var entry = scala.collection.mutable.HashMap[String, AnyRef]()
              entry += "title" -> msg.title.as[String]
              entry += "summary" -> msg.summary.as[String]
              entry += "text" -> msg.text.as[String]
            }
          }
          catch{
            // TODO: improve logging
            case e: Exception => println("Failed parsing consumer message offset=" + msgoffset.offset.toString)
          }

          if(Q.length % 100 == 0){
            println("Already enqueued "+Q.length.toString+" news")
          }

          while(Q.length > maximumQueueSize)
               java.lang.Thread.sleep(100)

        }
      }
    })
  fetcher_thread.setDaemon(true)
  fetcher_thread.start


  def receive = {
      case "get_news" => {
        //Wait foer news to arrive
        while(Q.isEmpty)
          java.lang.Thread.sleep(100)

        //Ok
         if(!Q.isEmpty) sender ! Item(Q.dequeue())
      }
  }
}


/*
* Basic class for tagger
*/
class BasicTaggerActor extends Actor{
  /*
  * Override in inhertiting classes
   */
   def tag(x: Map[String, AnyRef]){
     return List(x("uuid"), "ExampleTag1", "ExampleTag2")
   }

  /**
   * Override in inheriting classes
   */
   def getType(){
     return "BasicTagger"
   }

  def receive = {
    case Tag(x: Map[String, AnyRef]) =>
        sender ! Tagged(tag(x))
    case GetType => sender ! getType()
  }
}







object MantisMaster extends Actor {
  val taggersCount:Int =0
  val kafkaFetchersCounter: Int = 0
  var taggers = List()



  def start {
    //Define number of Taggers
    val taggersCount = 5
    //Kakfa fetchers, only one possible
    val kafkaFetchersCount = 1

    val system = ActorSystem("MantisShrimp")

    // Construct taggers
    var taggers = List()
    for(i <- 0 to taggersCount) taggers ::= system.actorOf(Props[BasicTaggerActor], name = ("taggerActor" + i.toString) )

    // KafkaFetcher thread
    val kafkaFetcher = system.actorOf(Props[MantisKafkaFetcherBasic], name = ("kafkaFetcher0") )



    // Run flow
    kafkaFetcher ! "get_news"
  }

  def receive = {
    case Tagged(x: List[String]) => {
        println(x.get(0)+ " tagged with "+x.mkString)
    }
    case Item(x: Map[String, AnyRef]) => {

    }
    case "start" => {
      start
    }
  }

}

object Main extends App{

  val system = ActorSystem("MantisShrimp")
  val mantisMaster = system.actorOf(Props[BasicTaggerActor], name = "mantisMaster")
  mantisMaster ! "start"
}