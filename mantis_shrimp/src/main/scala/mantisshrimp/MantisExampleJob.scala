package mantisshrimp

import akka.actor.{ActorRef, Actor}

/**
 * Created by staszek on 5/17/14.
 */
class MantisExampleJob extends Actor with MantisJobHandler {
   override def onAdd(mantisPath: String, actor: ActorRef){
        println("Added "+mantisPath)
   }

}
