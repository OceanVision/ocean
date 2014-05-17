/**
 * Main file running system
 */
package mantisshrimp

import akka.actor._
import ner._
import com.typesafe.config.ConfigFactory

//Rapture JSON parser
import rapture.json._
import jsonParsers.scalaJson._
import rapture.core._
import strategy.throwExceptions

import io.Source._
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

object MantisLiterals{
  val ParentMantisPath:String = "parentMantisPath"
  val ItemText = "text"
  val ItemSummary = "summary"
  val ItemTitle = "title"
  val ItemUUID = "uuid"
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
  def runActor(classname: String, parentMantisPath: String, configDump: String, name: String){

  }

  ///Runs system specified in this mantis shrimp node
  def runSystem2 = {
    //Run system as configured
    val system = ActorSystem(MantisConfiguration.actor_system_name)

    /*,
      ConfigFactory.parseString("""
                            akka.remote.netty.port = 9999
      """)
    )
    */

    //Read in node configuration
    val conf =
      JsonBuffer.parse(scala.io.Source.fromFile("mantis.conf").mkString)



    println(conf)
    println(conf(0).name)


    val config_map:  scala.collection.mutable.Map[String, String] = scala.collection.mutable.Map[String, String]()


    config_map(MantisLiterals.ParentMantisPath) = conf(0).parentMantisPath.as[String]
    
    //Start Master
    val master = system.actorOf(Props(new MantisMaster(config_map.toMap)), MantisConfiguration.mantis_master_name)

    config_map(MantisLiterals.ParentMantisPath) = conf(1).parentMantisPath.as[String]

    //Start example job
    val sample_job = system.actorOf(Props(new MantisExampleJob(config_map.toMap)), "example_job_1")


    sample_job ! SetMaster(master)



  }

  runSystem2

}