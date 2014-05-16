package mantisshrimp

//TODO: add checking Kafka spout


import akka.actor.{Actor, Props}


import rapture.io._
import rapture.json._


import kafka.consumer._

import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._

import scala.collection.mutable

//import kafka.producer.{ProducerConfig, ProducerData, Producer}

//Internal strategy for Rapture.io - I dont see this design choice..

import strategy.throwExceptions

import java.util.Properties

import scala.collection.JavaConverters._
import kafka.consumer.ConsumerConfig
import java.nio.file.{Paths, Files}

import akka.actor.{Actor, Props, ActorSystem}




import java.lang.{Runnable, Thread}

/**
 * Basic Kafka Actor. Note that it will be sufficient in most cases because
 * We will create new topics for new big chunks of news. I do not want
 * to focus on implementing this one single actor.
 */
class MantisNewsFetcherKafka extends Actor with MantisNewsFetcher {
  val topic: String = "mantis_mock_1"
  val tagged_topic: String = topic + "_tagged"

  //Encoding for JSON parsing
  implicit val enc = Encodings.`UTF-8`
  //Stop fetching thread when exceedes
  val maximumQueueSize = 100
  //Queue to store messages
  val Q = new mutable.SynchronizedQueue[scala.collection.mutable.Map[String, AnyRef]]()

  val taggedS: mutable.HashSet[String] = new mutable.HashSet[String] with mutable.SynchronizedSet[String]


  // Fetch already tagged news (note this will be synchronized through offsets
  // the more advanced version.
  val tagged_commited = if (Files.exists(Paths.get("tagged.dat")))
    scala.io.Source.fromFile("tagged.dat").mkString.split("\\r?\\n").toList
  else
    List()
  var tagged = scala.collection.mutable.Set[String]()
  tagged ++= tagged_commited

  /**
   * Commits already tagged to file. Not implemented correctly now (should update list)
   */
  private def commitTagged() = {
    val fw = new java.io.FileWriter("tagged.dat")
    try fw.write(tagged.mkString("/n"))
    finally fw.close()
  }

  // Fetching thread running in background
  val fetcher_thread = new java.lang.Thread(new java.lang.Runnable {
    def run() {
      while (true) {
        //Source: http://sillycat.iteye.com/blog/2015181
        // Prepare Kafka High Level Consumer. TODO: Create own wrapper around this
        val props = new Properties()
        props.put("group.id", topic + "_consumer")
        props.put("socket.receive.buffer.bytes", (2 * 1024 * 1024).toString)
        props.put("socket.timeout.ms", (ConsumerConfig.SocketTimeout).toString)
        props.put("fetch.message.max.bytes", (1024 * 1024).toString)
        props.put("fetch.min.bytes", (1).toString)
        props.put("fetch.wait.max.ms", (100).toString)
        props.put("auto.commit.enable", "true")
        props.put("auto.commit.interval.ms", (ConsumerConfig.AutoCommitInterval).toString)

        println("Connecting to zookeper "+DonCorleoneUtils.get_configuration_string("zookeeper","host") + ":" + DonCorleoneUtils.get_configuration_string("zookeeper","port"))

        props.put("auto.offset.reset", "smallest")
        props.put("zookeeper.connect",
          DonCorleoneUtils.get_configuration_string("zookeeper","host") + ":" + DonCorleoneUtils.get_configuration_string("zookeeper","port"))
        props.put("consumer.timeout.ms", (-1).toString)
        props.put("refresh.leader.backoff.ms", (ConsumerConfig.RefreshMetadataBackoffMs).toString)

        val consumerconfig = new ConsumerConfig(props)
        val consumer = kafka.consumer.Consumer.createJavaConsumerConnector(consumerconfig)
        val topicMap = Map[String, Integer](topic -> 1)
        val consumerMap = consumer.createMessageStreams(topicMap.asJava)
        val streamz = consumerMap.get(topic)
        val stream: KafkaStream[Array[Byte], Array[Byte]] = streamz.iterator().next()
        val consumerIter: ConsumerIterator[Array[Byte], Array[Byte]] = stream.iterator()

          val msgoffset = consumerIter.next()
          // Try parsing - if format is incorrect write error
          try {
            val msg = JsonBuffer.parse(new String(msgoffset.message))
            val uuid = msg.uuid.as[String]
            //TODO: improve
            if (!tagged.contains(uuid)) {
              var entry = scala.collection.mutable.HashMap[String, AnyRef]()
              //KafkaActor should act as a filter for garbage. It HAS to parse, and also
              //has to improve quality. Those are Unicode decoded from UTF-8!

              entry += "title" -> msg.title.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
              entry += "summary" -> msg.summary.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
              entry += "text" -> msg.text.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
              entry += "uuid" -> msg.uuid.as[String]
              Q.enqueue(entry)
            }

          }
          catch {
            case e: Exception => println("Failed parsing consumer message offset=" + msgoffset.offset.toString + " " + msgoffset.message.toString)
          }

          if (Q.length % 1000 == 0) {
            println("Already enqueued " + Q.length.toString + " news")
          }

          while (Q.length > maximumQueueSize)
            java.lang.Thread.sleep(1000)



      }
    }
  })
  fetcher_thread.setDaemon(true)
  fetcher_thread.start

  override def getNews(): scala.collection.mutable.Map[String, AnyRef] = {
    //Wait for news to arrive
    while (Q.isEmpty)
      java.lang.Thread.sleep(100)

    //Ok
    return Q.dequeue()
  }

  override def handleAlreadyTagged(uuid: String){
    tagged.add(uuid)
  }

}







