package mantisshrimp

import akka.actor.{ActorRef, Actor}

/**
 * Created by staszek on 5/17/14.
 */
class MantisExampleJob(config: Map[String, String]) extends Actor with MantisNode {

   val parentMantisPath: String = config(MantisLiterals.ParentMantisPath)

   override def onAdd(actor: ActorRef){
        println("Added "+ actor.path.name)
   }

  override def onSetMaster(_master:ActorRef){
    master = _master
    master ! Register(parentMantisPath)
    master ! GetRegisteredActors
  }

   override def receive = receiveMantisNode orElse {

     case RegisteredActors(nodes: Seq[ActorRef])    =>
     {
        logMaster("Registered actors in the system: "+nodes.toString)
     }

   }

}
