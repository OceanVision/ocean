/**
 * Main file running system
 */
package mantisshrimp

import akka.actor.{Props, ActorSystem}
import ner._


//TODO: write tests

object Main extends App{

  def runSystem = {
    val system = ActorSystem("mantisshrimp")
    val mantisMaster = system.actorOf(Props[MantisMaster], name = "mantisMaster")

    mantisMaster ! "start"
  }

   def nerTest = {
     val tg = new SevenClassNERTagger()
     println(tg.tag("Bruce Willis left apartment killing people"))
   }

  runSystem

}