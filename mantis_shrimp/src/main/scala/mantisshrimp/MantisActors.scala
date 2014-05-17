//TODO: add stacking traits

package mantisshrimp

import akka.actor.{ActorRef, Actor}
import mantisshrimp.GetType
import mantisshrimp.GetType


/*
* Basic Node. Accepts addition of sub-nodes, and decides when to run on itsel
*/
trait MantisNode extends Actor{
  var master: ActorRef = null
  val parentMantisPath: String
  val addedActors: scala.collection.mutable.ListBuffer[ActorRef] =
    new scala.collection.mutable.ListBuffer[ActorRef]


  //TODO: replace with some sensible logging
  def logStdOut(msg: String){
     println(context.self.path.name + "\t" + msg)
  }

  ///Return mantis path of Actor (simply stripped from unnecessary data for now)
  def getMantisPath(): String = {
    return context.self.path.name // TODO: Huge simplification
  }



  ///How to act on registration of new actor to this node
  def onAdd(actor:ActorRef){
      println(context.self.path + ":: added actor "+actor.path)
  }

  def onSetMaster(_master:ActorRef){
     master = _master
     master ! Register(parentMantisPath)
  }

  def receiveMantisNode: Receive = {
    case AddActor(actor) => {
      onAdd(actor)
    }
    case SetMaster(actor) => {
      onSetMaster(actor)
    }
  }

  def receive = receiveMantisNode
}

trait MantisNewsFetcher extends Actor{

  ///Returns news to tag
  def getNews(): scala.collection.mutable.Map[String, AnyRef]

  def handleAlreadyTagged(uuid: String): Unit

  ///Returns node type
  def getType(): String={
    return "NewsFetcher"
  }

  def receiveMantisNewsFetcher : Receive = {
    case "get_news" => {
      sender ! ItemArrive(getNews())
    }
    case AlreadyTagged(uuid) => {
      handleAlreadyTagged(uuid)
    }
    case GetType => sender ! getType()
  }


  def receive = receiveMantisNewsFetcher
}


/*
* Basic class for tagger
*/
trait MantisTagger extends Actor{

  ///Tag news
  def tag(x: scala.collection.mutable.Map[String, AnyRef]): Tuple2[String, Seq[MantisTag]] = {
    return (x("uuid").asInstanceOf[String], Seq[MantisTag](MantisTag("ExampleWord1", "ExampleTag1"),
      MantisTag("ExampleWord2","ExampleTag2")))
  }

  ///Returns type of the node
  def getType(): String={
    return "Tagger"
  }

  def receiveMantisTagger: Receive = {
    case Tag(x) => {
      val tag_result = tag(x)
      sender ! Tagged(tag_result._1, tag_result._2)  //should be possible withut unpacking..

    }
    case GetType => sender ! getType()

  }

  def receive = receiveMantisTagger
}