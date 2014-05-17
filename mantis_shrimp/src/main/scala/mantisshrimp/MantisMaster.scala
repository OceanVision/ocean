package mantisshrimp
import akka.actor.{ActorRef, Actor, Props}
import akka.actor

/**
 * Created by staszek on 5/16/14.
 */
class MantisMaster extends Actor with MantisJobHandler {
  var hasTagger = false
  var hasNewsFetcher = false
  var hasNeo4jDumper = false

  val registeredActors: scala.collection.mutable.ListBuffer[(String, ActorRef)] =
      new scala.collection.mutable.ListBuffer[(String, ActorRef)]




  registeredActors.prepend(("/", context.self))


  override def onAdd(mantisPath: String, actor: ActorRef){
    println("Added path "+actor.path)
  }

  println(self.path)



  def onRegister(mantisPath: String, actor: ActorRef){
    registeredActors.prepend((mantisPath, actor))
  }



  override def receive = {
    case AddActor(mantisPath, actor) => {
      onAdd(mantisPath, actor)
    }
    case Register(mantisPath, actor) => {
      onRegister(mantisPath, actor)
    }
    case GetRegisteredActors => {
      sender ! RegisteredActors(registeredActors.toSeq)
    }
  }

}
