//TODO: add stacking traits

package mantisshrimp

import akka.actor.{ActorRef, Actor}


object MantisNode{
  ///Helper function checking if given node type has given subtype
  def isOfType(mantisType: String, t: String): Boolean = {
      return mantisType.split("""\.""").foldLeft(false) {
        (z, i) => {
          z || i==t
        }
      }
  }
}
/*
* Basic Node. Accepts addition of sub-nodes, and decides when to run on itsel
*/
trait MantisNode extends Actor{
  var master: ActorRef = null
  val parentMantisPath: String
  val addedActors: scala.collection.mutable.ListBuffer[ActorRef] =
    new scala.collection.mutable.ListBuffer[ActorRef]


  //TODO: replace with some sensible logging
  def logSelf(msg: String){
     Main.mantisLogger.log(context.self.path.name + "::" + msg)
  }

  def logMaster(msg: String){
     master ! Log(msg)
  }

  /*
  * @return mantis type with each dot representing implementing interface/functionality. For instance
  *
  * MantisNode.MantisTagger.7NER - is a MantisTagger
   */
  def getMantisType(): String = {
     return MantisLiterals.MantisNode
  }

  logSelf("starting "+getMantisType())

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
    case GetMantisType => {
      sender ! MantisType(getMantisType())
    }
    case MantisType(mantisType) => {
      logMaster("not caught mantisType = "+mantisType)
    }
  }

  def receive = receiveMantisNode
}

trait MantisNewsFetcher extends Actor with MantisNode{

  ///Returns news to tag
  def getNews(): scala.collection.mutable.Map[String, AnyRef]

  def handleAlreadyTagged(uuid: String): Unit

  ///Returns node type
  override def getMantisType(): String={
    return MantisLiterals.MantisNode+"."+MantisLiterals.MantisNewsFetcher
  }

  def receiveMantisNewsFetcher : Receive = receiveMantisNode orElse {
    case GetNews => {
      sender ! ItemArrive(getNews())
    }
    case AlreadyTagged(uuid) => {
      handleAlreadyTagged(uuid)
    }

  }

  override def receive =  receiveMantisNewsFetcher
}

///Dumps news somewhere (for instance Neo4j database)
trait MantisNewsDumper extends Actor with MantisNode{

  ///Returns news to tag
  def dumpNews(uuid: String, tags: Seq[MantisTag])

  ///Returns node type
  override def getMantisType(): String={
    return MantisLiterals.MantisNode+"."+MantisLiterals.MantisNewsFetcher
  }

  def receiveMantisNewsFetcher : Receive = receiveMantisNode orElse {
    case Tagged(x, tags) => {
       dumpNews(x, tags)
    }

  }

  override def receive =  receiveMantisNewsFetcher
}



/*
* Basic class for tagger
*/
trait MantisTagger extends Actor with MantisNode{

  ///Tag news
  def tag(x: scala.collection.mutable.Map[String, AnyRef]): Tuple2[String, Seq[MantisTag]] = {
    return (x("uuid").asInstanceOf[String], Seq[MantisTag](MantisTag("ExampleWord1", "ExampleTag1"),
      MantisTag("ExampleWord2","ExampleTag2")))
  }

  ///Returns node type
  override def getMantisType(): String={
    return MantisLiterals.MantisNode+"."+MantisLiterals.MantisTagger
  }

  def receiveMantisTagger: Receive = receiveMantisNode orElse  {
    case Tag(x) => {
      val tag_result = tag(x)
      sender ! Tagged(tag_result._1, tag_result._2)  //should be possible withut unpacking..

    }
  }

  override def receive = receiveMantisTagger
}