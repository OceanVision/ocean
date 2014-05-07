package mantisshrimp

import akka.actor.Actor

/**
 * Created by staszek on 4/21/14.
 */

/*
* Basic class for tagger
*/


class BasicTaggerActor extends Actor{

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
    return "BasicTagger"
  }

  def receive = {
    case Tag(x) => {
      val tag_result = tag(x)
      sender ! Tagged(tag_result._1, tag_result._2)  //should be possible withut unpacking..

    }
    case GetType => sender ! getType()

  }
}