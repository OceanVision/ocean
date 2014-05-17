package mantisshrimp

import akka.actor.{ActorRef, Actor}


/*
* Basic job handler. Accepts registrations of sub jobs, and decides when to run on itself
*/
trait MantisJobHandler extends Actor{

  val myActors: scala.collection.mutable.ListBuffer[(String, ActorRef)] =
    new scala.collection.mutable.ListBuffer[(String, ActorRef)]

  ///How to act on registration of new actor to this node
  def onAdd(mantisPath:String, actor:ActorRef){

  }




  def receive = {
    case AddActor(mantisPath, actor) => {
      onAdd(mantisPath, actor)
    }
  }
}

trait MantisNewsFetcher extends Actor{

  /*
  * Override in inhertiting classes
   */
  def getNews(): scala.collection.mutable.Map[String, AnyRef]

  def handleAlreadyTagged(uuid: String): Unit

  /**
   * Override in inheriting classes
   */
  def getType(): String={
    return "NewsFetcher"
  }

  def receive = {
    case "get_news" => {
      sender ! ItemArrive(getNews())
    }
    case AlreadyTagged(uuid) => {
      handleAlreadyTagged(uuid)
    }
  }
}


/*
* Basic class for tagger
*/
trait MantisTagger extends Actor{

  /*
  * Override in inhertiting classes
   */
  def tag(x: scala.collection.mutable.Map[String, AnyRef]): Tuple2[String, Seq[MantisTag]] = {
    return (x("uuid").asInstanceOf[String], Seq[MantisTag](MantisTag("ExampleWord1", "ExampleTag1"),
      MantisTag("ExampleWord2","ExampleTag2")))
  }

  /**
   * Override in inheriting classes
   */
  def getType(): String={
    return "Tagger"
  }

  def receive = {
    case Tag(x) => {
      val tag_result = tag(x)
      sender ! Tagged(tag_result._1, tag_result._2)  //should be possible withut unpacking..

    }
    case GetType => sender ! getType()

  }
}