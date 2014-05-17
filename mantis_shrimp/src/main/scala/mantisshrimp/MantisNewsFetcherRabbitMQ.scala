package mantisshrimp


import com.rabbitmq.client._
import akka.actor.{Actor, Props}
import rapture.io._
import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import scala.collection.mutable
import strategy.throwExceptions
import java.nio.file.{Paths, Files}

import akka.actor.{Actor, Props, ActorSystem}


object RabbitMQConnection {

  private val connection: Connection = null;

  /**
   * Return a connection if one doesn't exist. Else create
   * a new one
   */
  def getConnection(): Connection = {
    connection match {
      case null => {
        val factory = new ConnectionFactory();
        factory.setHost("localhost");
        factory.setUsername("admin");
        factory.setPassword("password");
        factory.newConnection();
      }
      case _ => connection
    }
  }
}

/**
 * Fetching news from RabbitMQ
 */
class MantisNewsFetcherRabbitMQ(config: Map[String, String]) extends Actor with MantisNewsFetcher {
  val parentMantisPath = config(MantisLiterals.ParentMantisPath)

  val queue: String = "mantis_totag"
  //Encoding for JSON parsing
  implicit val enc = Encodings.`UTF-8`
  //Stop fetching thread when exceedes
  val maximumQueueSize = 100
  //Queue to store messages
  val Q = new mutable.SynchronizedQueue[scala.collection.mutable.Map[String, AnyRef]]()
  val rabbitMqMetaData: mutable.HashMap[String, QueueingConsumer.Delivery] = new mutable.HashMap[String, QueueingConsumer.Delivery]

  val connection = RabbitMQConnection.getConnection()
  val fetchingChannel = connection.createChannel()


  // Fetching thread running in background
  val fetcher_thread = new java.lang.Thread(new java.lang.Runnable {
    def run() {
      val consumer = new QueueingConsumer(fetchingChannel)

      fetchingChannel.basicConsume(queue, false, consumer)

      while (true) {
        val delivery = consumer.nextDelivery();

        val msg_raw = new String(delivery.getBody());
        // Try parsing - if format is incorrect write error
        try {

          val msg = JsonBuffer.parse(msg_raw)
          val uuid = msg.uuid.as[String]

            var entry = scala.collection.mutable.HashMap[String, AnyRef]()
            //KafkaActor should act as a filter for garbage. It HAS to parse, and also
            //has to improve quality. Those are Unicode decoded from UTF-8!

            entry += "title" -> msg.title.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "summary" -> msg.summary.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "text" -> msg.text.as[String].split("\\r?\\n").map(_.trim).mkString(" ")
            entry += "uuid" -> msg.uuid.as[String]


            rabbitMqMetaData(msg.uuid.as[String]) = delivery

            Q.enqueue(entry)


        }
        catch {
          case e: Exception => println("Failed parsing consumer message "+msg_raw)
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
    fetchingChannel.basicAck(rabbitMqMetaData(uuid).getEnvelope().getDeliveryTag(), false)
    rabbitMqMetaData.remove(uuid)
  }

}


