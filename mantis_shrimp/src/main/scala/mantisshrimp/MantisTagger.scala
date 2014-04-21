package mantisshrimp

import akka.actor.Actor

/**
 * Created by staszek on 4/21/14.
 */
case class Tag(x: scala.collection.mutable.Map[String, AnyRef])
case class GetType
/*
* Basic class for tagger
*/
class BasicTaggerActor extends Actor{


  /*
  * Override in inhertiting classes
   */
  def tag(x: scala.collection.mutable.Map[String, AnyRef]): List[String] = {
    return List[String](x("uuid").asInstanceOf[String], "ExampleTag1", "ExampleTag2")
  }

  /**
   * Override in inheriting classes
   */
  def getType(): String={
    return "BasicTagger"
  }

  def receive = {
    case Tag(x) =>
      sender ! Tagged(tag(x))
    case GetType => sender ! getType()

  }
}