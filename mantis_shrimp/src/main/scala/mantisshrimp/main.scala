/**
 * Main file running system
 */
package mantisshrimp

import akka.actor._
import ner._
import com.typesafe.config.ConfigFactory
import java.lang.Exception

//Rapture JSON parser
import rapture.json._
import jsonParsers.scalaJson._
import rapture.core._
import strategy.throwExceptions

import io.Source._
import rapture.io._
import rapture.core._
import rapture.json._

import akka.actor._
import akka.pattern.ask

import scala.concurrent.duration._
import scala.concurrent.Await
import scala.concurrent.Await
import scala.concurrent.Future


object MantisLiterals{
  val ParentMantisPath:String = "parentMantisPath"
  val Classname = "classname"
  val UniqueName = "unique_name"
  val GuardianActor = "user"

  val ItemText = "text"
  val ItemSummary = "summary"
  val ItemTitle = "title"
  val ItemUUID = "uuid"
}

case class Config(host_master: String = "localhost",
port_master: Int= 2552, port: Int = 2552, host: String = "localhost",
actor_system_name: String = "MantisShrimp", mantis_master_name: String = "mantis_master",
config_path: String = "mantis.conf"
                   )



object Main extends App{
  //Encoding for JSON parsing
  implicit val enc = Encodings.`UTF-8`

  //Master has to be created or fetched from existing cluster. It is sent by SetMaster function
  var system: akka.actor.ActorSystem  = null
  var master: akka.actor.ActorRef = null


  //Parse configuration
  val parser = new scopt.OptionParser[Config]("scopt") {
    head("scopt", "3.x")
    opt[String]('h', "host_master") action { (x, c) =>
      c.copy(host_master = x) } text("Host where is located ActorSystem with master")
    opt[Int]('p', "port_master")  action { (x, c) =>
      c.copy(port_master = x) } text("Port where is located ActorSystem with master")
    opt[String]('c', "host") action { (x, c) =>
      c.copy(host = x) } text("Host to which is binding ActorSystem. Default localhost")
    opt[Int]('m', "port")  action { (x, c) =>
      c.copy(port = x) } text("Port to which is binding ActorSystem. Default 2552")
    opt[String]('l', "actor_system_name")  action { (x, c) =>
      c.copy(actor_system_name = x) } text("Actor System Name - do not change unless you know what you are doing" )
    opt[String]('l', "mantis_master_name")  action { (x, c) =>
      c.copy(mantis_master_name = x) } text("Master in the system - has to match across whole cluster - do not change unless you know what you are doing" )
    opt[String]('l', "config_path") action { (x, c) =>
      c.copy(config_path = x) } text("Path to config file" )

  }
  var config: Config = Config()
  parser.parse(args, Config()) map { _config =>
    config = _config
  } getOrElse {
    println("Failed parsing parameters. Please see help")
    sys.exit(1)
  }
  




  def runSystem = {
    val system = ActorSystem(config.actor_system_name)
    val mantisMaster = system.actorOf(Props[MantisTaggerCoordinator], name = "mantisMaster")

    mantisMaster ! "start"
  }

   def nerTest = {
     val tg = new SevenClassNERTagger()
     println(tg.tag("Bruce Willis left apartment killing people"))
   }



  ///Runs system specified in this mantis shrimp node
  def runMantisShrimp = {
    //Run system as configured
    val port = config.port
    val hostname = config.host

    val config_string = s"""
        akka {
            actor {
              provider = "akka.remote.RemoteActorRefProvider"
            }
            remote {
                enabled-transports = ["akka.remote.netty.tcp"]
                netty.tcp {
                  hostname = $hostname
                  port = $port
               }
            }
            }
    """

    //Create system
    system = ActorSystem(config.actor_system_name,
      ConfigFactory.load(ConfigFactory.parseString(config_string)))


    //Read in node configuration
    var conf: List[Map[String, String]] = null //TODO: prettier handling
    try {
       conf = JsonBuffer.parse(scala.io.Source.fromFile(config.config_path).mkString).as[List[Map[String, String]]]
    }catch{
      case exception: Throwable => {
          println("Failed reading in configuration file with "+exception.toString)
          sys.exit(1)
      }
    }



    if(config.host_master != config.host || config.port_master != config.port) {

      val masterPath = "akka.tcp://%s@%s:%s/%s/%s".format(config.actor_system_name, config.host_master,
        config.port_master, MantisLiterals.GuardianActor, config.mantis_master_name)


      println("Connecting to MantisMaster at " + masterPath)
      //Fetch master  (requires akka.actor >= 2.2.1)
      val future_master_ref = system.actorSelection(masterPath).resolveOne(10.second)

      println("Fetching master actor in provided cluster configuration")
      try {
        master = Await.result(future_master_ref, 10.second)
        println("Fetched succesfully MantisMaster! " + master.toString)


      }
      catch {
        case t: Throwable => {
          println("Failed to fetch master reference with error " + t.toString)
          sys.exit(1)
        }
      }

    }

//
//    //Ensure validity of configuration (TODO: export to validate fnc)
//    if(config.host_master == "localhost" || config.host_master == "127.0.0.1"){
//
//        assert(config.host == config.host_master && config.port == config.port_master,
//          "Not matching host_master and host, or port_master and port")
//    }else {
//
//    }


    //Run actors
    for(actorConfiguration:Map[String, String] <- conf){
       try {
         runActor(actorConfiguration(MantisLiterals.Classname),
           actorConfiguration(MantisLiterals.UniqueName),
           actorConfiguration)
       } catch{
         case exc: Throwable => {
            println("Failed running Actor with "+exc.toString)
            sys.exit(1)
         }
       }
    }





    ///Runs given actor
    def runActor(classname: String, actor_name: String, actor_config: Map[String, String])
    = classname match {
        case "MantisMaster" => {
            master = system.actorOf(Props(new MantisMaster(actor_config.toMap)), config.mantis_master_name)
        }
        case "MantisExampleJob" => {
          //TODO:Apparently reflection for non-parameterless constructors is harder
          val sample_job = system.actorOf(Props(new MantisExampleJob(actor_config.toMap)), actor_name)
          sample_job ! SetMaster(master)
        }
    }



  }

  runMantisShrimp

}