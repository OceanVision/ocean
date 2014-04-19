package mantis_shrimp

import akka.actor.{Actor, Props, ActorSystem}

class HelloActor extends Actor {
  def receive = {
    case "hello" => println("hello back at you")
    case _       => println("huh?")
  }
}

object Main {
  def main(a: Array[String]) {

      val system = ActorSystem("HelloSystem")
      // default Actor constructor
      val helloActor = system.actorOf(Props[HelloActor], name = "helloactor")
      helloActor ! "hello"
      helloActor ! "buenos dias2"
  }
}