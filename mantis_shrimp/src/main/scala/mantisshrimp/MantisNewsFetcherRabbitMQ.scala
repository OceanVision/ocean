package mantisshrimp


import com.rabbitmq.client._
import akka.actor.Actor
import rapture.io._
import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import scala.collection.mutable
import strategy.throwExceptions
import java.nio.file.{Paths, Files}

import akka.actor.{Actor, Props, ActorSystem}
import mantisshrimp.utils.RabbitMQConnection


/**
 * Fetching news from RabbitMQ
 */
class MantisNewsFetcherRabbitMQ(config: Map[String, String]) extends Actor with MantisNewsFetcher {
  val parentMantisPath = config(MantisLiterals.ParentMantisPath)

  val queue: String = "mantis_totag"
  //Encoding for JSON parsing
  implicit val enc = Encodings.`UTF-8`
  //Stop fetching thread when exceedes
  val maximumQueueSize = 10
  //Queue to store messages
  val Q = new mutable.SynchronizedQueue[scala.collection.mutable.Map[String, AnyRef]]()
  val rabbitMqMetaData: mutable.HashMap[String, Long] = new mutable.HashMap[String, Long]

  val connection = RabbitMQConnection.getConnection()
  val fetchingChannel = connection.createChannel()


  // Fetching thread running in background
  val fetcher_thread = new java.lang.Thread(new java.lang.Runnable {
    def run() {
      val consumer = new QueueingConsumer(fetchingChannel)

      //TODO: set to false and correct bug
      val auto_ack = false
      fetchingChannel.basicConsume(queue, auto_ack, consumer)


      var fetched_count = 0

      while (true) {
        val delivery = consumer.nextDelivery();

        val msg_raw = new String(delivery.getBody());
        // Try parsing - if format is incorrect write error
        try {

          fetched_count += 1

          if(fetched_count % 100 == 0)
            logSelf("Fetched already "+fetched_count.toString)


          val msg = JsonBuffer.parse(msg_raw)
          val uuid = msg.uuid.as[String]

            var entry = scala.collection.mutable.HashMap[String, AnyRef]()
            //KafkaActor should act as a filter for garbage. It HAS to parse, and also
            //has to improve quality. Those are Unicode decoded from UTF-8!

            entry += "title" -> msg.title.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "summary" -> msg.summary.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "text" -> msg.text.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "uuid" -> msg.uuid.as[String]


            rabbitMqMetaData(msg.uuid.as[String]) = delivery.getEnvelope().getDeliveryTag()

            Q.enqueue(entry)


        }
        catch {
          case e: Exception => println("Failed parsing consumer message "+msg_raw)
        }

        if (Q.length % maximumQueueSize == 0) {
          println(rabbitMqMetaData.toString())

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
    //Try because if we have tagged 2 times same news it doesn't matter
    try {
      fetchingChannel.basicAck(rabbitMqMetaData(uuid), false)
      rabbitMqMetaData.remove(uuid)
    }
    catch{
      case e: Throwable => {

      }
    }
  }

}


