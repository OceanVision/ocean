package com.lionfish.server

import com.lionfish.utils.Config
import com.lionfish.logging.Logging

object Launcher {
  private val log = Logging

  private def configure(args: Array[String]) = {
    var debug = false
    var customPort = false
    for (item <- args) {
      val arg = item.split("=")
      arg(0) match {
        case "--debug" => {
          try {
            if (!customPort) {
              Config.serverAddress = "localhost"
              Config.serverPort = 7777
              debug = true
              log.info("Running in the debug mode (port: 7777).")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Custom port already set or invalid parameter: debug.")
          }
        }
        case "--port" => {
          try {
            val value = arg(1).toInt
            if (value > 0 && !debug) {
              Config.serverPort = arg(1).toInt
              customPort = true
              log.info(s"Using custom server port: $value.")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Debug mode already set or invalid parameter: port.")
          }
        }
        case "--neo4j-path" => {
          try {
            val value = arg(1)
            Config.neo4jPath = value
            log.info(s"Using Neo4j custom path: $value.")
          } catch {
            case e: Exception => log.info("Invalid parameter: neo4j-path.")
          }
        }
        case "--neo4j-console-port" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.neo4jConsolePort = arg(1).toInt
              log.info(s"Using custom Neo4j console port: $value.")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Invalid parameter: neo4j-console-port.")
          }
        }
        case "--use-cache" => {
          try {
            Config.useCache = true
            log.info("Using cache.")
          } catch {
            case e: Exception => log.info("Custom port already set or invalid parameter: debug.")
          }
        }
        case "--cache-port" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.cachePort = arg(1).toInt
              log.info(s"Using custom cache port: $value.")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Invalid parameter: neo4j-console-port.")
          }
        }
        case "--num-of-request-handlers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfRequestHandlers = value
              log.info(s"Using custom number of request handlers ($value).")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Invalid parameter: num-of-request-handlers.")
          }
        }
        case "--num-of-cache-workers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfCacheWorkers = value
              log.info(s"Using custom number of cache workers ($value).")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Invalid parameter: num-of-cache-workers.")
          }
        }
        case "--num-of-db-workers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfDatabaseWorkers = value
              log.info(s"Using custom number of database workers ($value).")
            } else {
              throw new Exception()
            }
          } catch {
            case e: Exception => log.info("Invalid parameter: num-of-db-workers.")
          }
        }
      }
    }
  }

  def main(args: Array[String]) = {
    configure(args)
    new Thread(Server).start()
  }
}
