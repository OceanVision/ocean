package mantisshrimp
import akka.actor.{ActorRef, Actor}

/**
 * Created by staszek on 5/16/14.
 */
class MantisMaster(config: Map[String, String]) extends Actor with MantisNode {
  val parentMantisPath: String = ""


  val registeredActors: scala.collection.mutable.ListBuffer[ActorRef] =
      new scala.collection.mutable.ListBuffer[ActorRef]

  registeredActors.prepend(context.self)


  override def onAdd(actor: ActorRef){
    logSelf("Added path "+actor.path)
    addedActors.prepend(actor)

  }



  def onRegister(parentMantisPath: String, registrant_actor: ActorRef){
    logSelf("Registered path "+registrant_actor.path)

    //Find target actor
    for(a <- registeredActors){
       //Note: In first iteration we are assuming here 1 level registration and we are
       //not switching parents. TODO: improve
       if(a.path.name == parentMantisPath){
            a ! AddActor(registrant_actor)
       }
    }

    registeredActors.prepend(registrant_actor)
  }



   override def receive =
    receiveMantisNode orElse  {
        case Register(mantisPath) => {
          onRegister(mantisPath, sender)
        }
        case GetRegisteredActors => {
          sender ! RegisteredActors(registeredActors.toSeq)
        }
        case Log(msg: String) => {
          Main.mantisLogger.log(sender.path.name+"::"+msg)
        }
        case Identify => {
          sender ! ActorIdentity
        }
    }

}
