package mantisshrimp

import akka.actor.{Props, ActorSystem}


object Main extends App{
  val system = ActorSystem("mantisshrimp")
  val mantisMaster = system.actorOf(Props[MantisMaster], name = "mantisMaster")

  mantisMaster ! "start"
}