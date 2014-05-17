package mantisshrimp
import akka.actor._

/**
 * Created by staszek on 4/21/14.
 */

case class MantisTag(words: String, tag: String)


/* Messages used in the MantisShrimp system */

//Sent by MantisTagger with tagged news
case class Tagged(uuid: String, x:  Seq[MantisTag])

//Sent to MantisNewsFetcher trait to inform that news is processed 100% sure
case class AlreadyTagged(uuid: String)

//Returns type of node
case class GetType

//
case class ItemArrive(x: scala.collection.mutable.Map[String, AnyRef])

//Sent to MantisTagger trait Actor
case class Tag(x: scala.collection.mutable.Map[String, AnyRef])

//Register new node in the system. Will propagate down the system
case class Register(parentMantisPath: String)

//Add new node to actor. Will propagate down the system
case class AddActor(actor: ActorRef)

//Retrieve all registered nodes in the form of list of tuples (akkaPath, name, actor)
case class GetRegisteredActors()

//Answer to GetRegisteredNodes
case class RegisteredActors(nodes: Seq[ActorRef])

//Every non-master node will receive this message
case class SetMaster(master: ActorRef)
