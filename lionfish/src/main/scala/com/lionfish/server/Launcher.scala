package com.lionfish.server

import java.net._
import akka.actor._
import com.typesafe.config.ConfigFactory
import com.lionfish.utils.Config

object Launcher {
  private def parseParams(args: Array[String]): Map[String, Any] = {
    var result: Map[String, Any] = Map()
    for (item <- args) {
      val arg = item.split("=")
      arg(0) match {
        case "--debug" => {
          result += "debug" -> null
        }
        case "--port" => {
          try {
            result += "port" -> arg(1).toInt
          } catch {
            case e: Exception => println("Invalid parameter: port")
          }
        }
        case "--neo4j-path" => {
          try {
            result += "neo4j-path" -> arg(1)
          } catch {
            case e: Exception => println("Invalid parameter: neo4j-path")
          }
        }
        case "--neo4j-console-port" => {
          try {
            result += "neo4j-console-port" -> arg(1).toInt
          } catch {
            case e: Exception => println("Invalid parameter: neo4j-console-port")
          }
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
      Server.port = 7777
    } else if (params.contains("port")) {
      Server.port = params("port").asInstanceOf[Int]
    }

    if (params.contains("neo4j-path")) {
      var neo4jPath = params("neo4j-path").asInstanceOf[String]
      if (neo4jPath(neo4jPath.length - 1) == '/') {
        neo4jPath = neo4jPath.substring(0, neo4jPath.length - 1)
      }

      DatabaseManager.setNeo4jPath(neo4jPath)
    }

    if (params.contains("neo4j-console-port")) {
      DatabaseManager.setNeo4jConsolePort(params("neo4j-console-port").asInstanceOf[Int])
    }

    DatabaseManager
    new Thread(Server).start()
  }
}
