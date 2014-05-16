package mantisshrimp

/**
 * Created by staszek on 4/21/14.
 */
//Messages for Akka system
case class MantisTag(words: String, tag: String)
case class Tagged(uuid: String, x:  Seq[MantisTag])
case class AlreadyTagged(uuid: String)
case class ItemArrive(x: scala.collection.mutable.Map[String, AnyRef])
case class Tag(x: scala.collection.mutable.Map[String, AnyRef])
case class GetType
case class Register(name: String)


object MantisLiterals{
    val ItemText = "text"
    val ItemSummary = "summary"
    val ItemTitle = "title"
    val ItemUUID = "uuid"
}