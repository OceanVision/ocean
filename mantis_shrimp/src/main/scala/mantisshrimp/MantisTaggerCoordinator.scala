package mantisshrimp


import akka.actor.{ActorRef, Actor}
import akka.pattern.ask

import scala.concurrent._
import scala.concurrent.duration._

import java.util.concurrent.locks.{ReadWriteLock, ReentrantReadWriteLock}

import akka.util.Timeout

/**
 * Created by staszek on 4/21/14.
 */


/*
* Node that can own several different MantisTaggers and single MantisNewsFetcher
 */
class MantisTaggerCoordinator(config: Map[String, String]) extends Actor with MantisNode{



  val parentMantisPath = config(MantisLiterals.ParentMantisPath)

  val taggersCount:Int =0
  val kafkaFetchersCounter: Int = 0

  val actorsLock: ReadWriteLock = new ReentrantReadWriteLock ()

  var currentTagger = monifu.concurrent.atomic.AtomicInt(0)

  var newsFetcher: ActorRef = null
  var taggers = List[akka.actor.ActorRef]()

  override def getMantisType(): String = {
      return "MantisNode.MantisTaggerCoordinator"
  }


  def ready(): Boolean = {
     return newsFetcher != null && taggers.length > 0
  }

  override def  onAdd(actor:ActorRef){

        try {
          actorsLock.writeLock().lock()
          logMaster("adding "+actor.toString)
          implicit val timeout = Timeout(5 seconds)
          val mantisType = Await.result(actor ? GetMantisType, 5 seconds).
            asInstanceOf[MantisType].mantisType
            logSelf("adding type resolved "+mantisType)

            if(MantisNode.isOfType(mantisType, MantisLiterals.MantisTagger)){
               logSelf("Received MantisTagger")
               taggers = actor :: taggers
            }else if(MantisNode.isOfType(mantisType, MantisLiterals.MantisNewsFetcher)){
               logSelf("Received MantisNewsFetcher")
               newsFetcher = actor
            }else{
              logMaster("ERROR not recognized actor.Shutting down!")
              sys.exit(1)
            }

            if(ready()) {
              logMaster("ready")
              //TODO: improve flow
              newsFetcher ! GetNews
            }
        }
        catch{
          case t: Exception => {
              logMaster("ERROR::failed to retrieve type from "+actor.toString +" error "+t.toString)

          }
        }
        finally{
           actorsLock.writeLock().unlock()
        }

  }

  var tagged = 0
  override def receive = receiveMantisNode orElse {
    case Tagged(uuid, x) => {
      tagged += 1
      if(tagged % 100 == 0)
        logMaster(uuid + " tagged with " + x.mkString + " from "+sender.path)

      newsFetcher ! AlreadyTagged(uuid.toString)
    }
    case ItemArrive(x) => {
      actorsLock.readLock().lock()
        //Should tag it with all taggers types. For now just call one in queue

        val currentTaggerLocal = currentTagger.getAndIncrement() % this.taggers.length

        taggers(currentTaggerLocal) ! Tag(x)

        sender ! GetNews
      actorsLock.readLock().unlock()
    }
  }

}