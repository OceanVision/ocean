package com.coral.connector

import com.coral.utils.Config

object Launcher {
  private def configure(args: Array[String]) = {
    for (item <- args) {
      val arg = item.split("=")
      arg(0) match {
        case "--num-of-request-handlers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfRequestHandlers = value
            }
          } catch {
            case e: Exception => println("Invalid parameter: num-of-request-handlers")
          }
        }
        case "--num-of-cache-workers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfCacheWorkers = value
            }
          } catch {
            case e: Exception => println("Invalid parameter: num-of-cache-workers")
          }
        }
        case "--num-of-db-workers" => {
          try {
            val value = arg(1).toInt
            if (value > 0) {
              Config.numberOfDatabaseWorkers = value
            }
          } catch {
            case e: Exception => println("Invalid parameter: num-of-db-workers")
          }
        }
      }
    }
  }

  def main(args: Array[String]) = {
    configure(args)
    new Thread(WebserviceConnector).start()
  }
}
