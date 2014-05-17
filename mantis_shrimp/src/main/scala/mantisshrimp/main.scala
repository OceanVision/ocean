/**
 * Main file running system
 */
package mantisshrimp

import akka.actor.{Props, ActorSystem}
import ner._
import com.typesafe.config.ConfigFactory

//Rapture JSON parser
import rapture.json._
import jsonParsers.scalaJson._
import rapture.core._
import strategy.throwExceptions

import io.Source._
import akka.actor.{Actor, Props}
import rapture.io._
import rapture.core._
import rapture.json._

///Stores configuration for given node. Pulled from DonCorleone
object MantisConfiguration{
  val host_master = "localhost"
  val port_master = 2552
  val actor_system_name = "MantisShrimp"
  val mantis_master_name = "mantis_master"
  val configuration_file = "mantis.conf"
}

object Main extends App{
  //Encoding for JSON parsing
  implicit val enc = Encodings.`UTF-8`

  def runSystem = {
    val system = ActorSystem(MantisConfiguration.actor_system_name)
    val mantisMaster = system.actorOf(Props[MantisTaggerCoordinator], name = "mantisMaster")

    mantisMaster ! "start"
  }

   def nerTest = {
     val tg = new SevenClassNERTagger()
     println(tg.tag("Bruce Willis left apartment killing people"))
   }


  ///Runs given actor
  def runActor(classname: String, akkaPath: String, configDump: String, name: String){

  }

  ///Runs system specified in this mantis shrimp node
  def runSystem2 = {
    //Run system as configured
    val system = ActorSystem(MantisConfiguration.actor_system_name,
      ConfigFactory.parseString("""
                            akka.remote.netty.port = 9999
      """)
    )

    //Read in node configuration
    val conf =
      JsonBuffer.parse(fromInputStream(getClass.getResourceAsStream(MantisConfiguration.configuration_file)).mkString)



    println(conf)
    println(conf(0).name)



  }

  runSystem2

}