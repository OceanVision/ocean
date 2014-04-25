package mantisshrimp


import akka.actor.{Props, ActorSystem, Actor}
import scala.collection.mutable

import monifu.concurrent._

/**
 * Created by staszek on 4/21/14.
 */



class MantisMaster extends Actor {

  val taggersCount:Int =0
  val kafkaFetchersCounter: Int = 0
  var taggers = List[akka.actor.ActorRef]()
  var currentTagger = monifu.concurrent.atomic.AtomicInt(0)


  def start {
    //Define number of Taggers
    val taggersCount = 5
    //Kakfa fetchers, only one possible
    val kafkaFetchersCount = 1
    //Create ActorSystem
    val system = ActorSystem("mantisshrimp")

    // Construct taggers
    for(i <- 0 to taggersCount) taggers = system.actorOf(Props[Mantis7ClassNERTagger], name = ("taggerActor" + i.toString) ) :: taggers

    // KafkaFetcher thread
    val kafkaFetcher = system.actorOf(Props[MantisKafkaFetcherBasic], name = ("kafkaFetcher0") )

    // Run flow
    kafkaFetcher ! "get_news"
  }

  def receive = {
    case Tagged(uuid, x) => {
      println(uuid + " tagged with " + x.mkString)
    }
    case ItemArrive(x) => {
      //Should tag it with all taggers types. For now just call one in queue
      println("News arrived")

      val currentTaggerLocal = currentTagger.getAndIncrement() % this.taggers.length

      taggers(currentTaggerLocal) ! Tag(x)

      sender ! "get_news"
    }
    case "start" => {
      start
    }
  }

}