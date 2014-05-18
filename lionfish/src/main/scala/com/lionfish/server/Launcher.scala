package com.lionfish.server

import java.net._
import akka.actor._
import com.typesafe.config.ConfigFactory
import com.lionfish.utils.Config

object Launcher {
  private val serverAddress = "localhost"
  private var serverPort = Config.defaultServerPort

  def getServerAddress: String = {
    serverAddress
  }

  def getServerPort: Int = {
    serverPort
  }

  private def parseParams(args: Array[String]): Map[String, Any] = {
    var result: Map[String, Any] = Map()
    for (item <- args) {
      val arg = item.split("=")
      arg(0) match {
        case "--port" => {
          try {
            result += "port" -> arg(1).toInt
          } catch {
            case e: Exception => println("Invalid parameter: port")
          }
        }
        case "--debug" => {
          result += "debug" -> null
        }
      }
    }

    result
  }

  def main(args: Array[String]) = {
    // Parses params
    val params = parseParams(args)

    // Sets params
    if (params.contains("debug")) {
      serverPort = 7777
    }

    if (params.contains("port")) {
      serverPort = params("port").asInstanceOf[Int]
    }

    // Creates remote proxy worker
//    val config = ConfigFactory.load("proxySystem")
//    val portConfig = ConfigFactory.parseString(s"akka.remote.netty.tcp.port = $serverPort")
//    val proxySystem = ActorSystem("proxySystem", portConfig.withFallback(config))
//    proxySystem.actorOf(Props(new Server), "proxy")
    Server.port = serverPort
    new Thread(Server).start()
  }
}
