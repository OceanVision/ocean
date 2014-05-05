package com.lionfish.server

import java.net.Socket
import com.lionfish.utils.IO

class Connection(private val id: Int,
                 private implicit val socket: Socket) extends Runnable {
  println(s"Client $id connected.")

  private def disconnect() = {
    try {
      socket.close()
      println(s"Client $id disconnected.")
    } catch {
      case e: Exception => {
        println(s"Client $id failed to disconnect. Error message: $e")
      }
    }
  }

  private def executeBatch(request: Map[String, Any]): List[Any] = {
    try {
      val count = request("count").asInstanceOf[Int]
      val tasks = request("tasks").asInstanceOf[Map[String, List[List[Any]]]]

      var response: List[Any] = List.fill(count.toInt)(null)
      for ((funcName, params) <- tasks) {
        var fullArgs: List[Map[String, Any]] = List()
        for (item <- params) {
          fullArgs = fullArgs :+ item(0).asInstanceOf[Map[String, Any]]
        }

        println(s"Client $id executes $funcName in batch.")

        // TODO: Solve this with reflection
        var rawResult: List[Any] = null
        funcName match {
          case "getByUuid" => {
            rawResult = DatabaseManager.getByUuid(fullArgs)
          }
          case "getByLink" => {
            rawResult = DatabaseManager.getByLink(fullArgs)
          }
          case "getModelNodes" => {
            rawResult = DatabaseManager.getModelNodes(fullArgs)
          }
          case "getChildren" => {
            rawResult = DatabaseManager.getChildren(fullArgs)
          }
          case "getInstances" => {
            rawResult = DatabaseManager.getInstances(fullArgs)
          }
          case "setProperties" => {
            rawResult = DatabaseManager.setProperties(fullArgs)
          }
          case "deleteProperties" => {
            rawResult = DatabaseManager.deleteProperties(fullArgs)
          }
          case "createNodes" => {
            rawResult = DatabaseManager.createNodes(fullArgs)
          }
          case "deleteNodes" => {
            rawResult = DatabaseManager.deleteNodes(fullArgs)
          }
          case "createRelationships" => {
            rawResult = DatabaseManager.createRelationships(fullArgs)
          }
          case "deleteRelationships" => {
            rawResult = DatabaseManager.deleteRelationships(fullArgs)
          }
          case "setRelationshipProperties" => {
            rawResult = DatabaseManager.setRelationshipProperties(fullArgs)
          }
          case "deleteRelationshipProperties" => {
            rawResult = DatabaseManager.deleteRelationshipProperties(fullArgs)
          }
          case _ => throw new NoSuchMethodException(funcName)
        }

        if (rawResult != null) {
          for (i <- 0 to rawResult.length - 1) {
            response = response.updated(params(i)(1).asInstanceOf[Int], rawResult(i))
          }
        }
      }

      response
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Client $id failed to execute a batch at line $line. Error message: $e")
      }
      List()
    }
  }

  private def executeFunction(request: Map[String, Any]): Any = {
    try {
      val funcName = request("funcName").asInstanceOf[String]
      val args = List(request("args").asInstanceOf[Map[String, Any]])

      println(s"Client $id executes $funcName.")

      // TODO: Solve this with reflection
      var response: List[Any] = null
      funcName match {
        case "getByUuid" => {
          response = DatabaseManager.getByUuid(args)
        }
        case "getByLink" => {
          response = DatabaseManager.getByLink(args)
        }
        case "getModelNodes" => {
          response = DatabaseManager.getModelNodes(args)
        }
        case "getChildren" => {
          response = DatabaseManager.getChildren(args)
        }
        case "getInstances" => {
          response = DatabaseManager.getInstances(args)
        }
        case "setProperties" => {
          response = DatabaseManager.setProperties(args)
        }
        case "deleteProperties" => {
          response = DatabaseManager.deleteProperties(args)
        }
        case "createNodes" => {
          response = DatabaseManager.createNodes(args)
        }
        case "deleteNodes" => {
          response = DatabaseManager.deleteNodes(args)
        }
        case "createRelationships" => {
          response = DatabaseManager.createRelationships(args)
        }
        case "deleteRelationships" => {
          response = DatabaseManager.deleteRelationships(args)
        }
        case "setRelationshipProperties" => {
          response = DatabaseManager.setRelationshipProperties(args)
        }
        case "deleteRelationshipProperties" => {
          response = DatabaseManager.deleteRelationshipProperties(args)
        }
        case _ => throw new NoSuchMethodException(funcName)
      }

      if (response != null && response.length > 0) {
        response(0)
      } else {
        null
      }
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Client $id failed to execute a function at line $line. Error message: $e")
      }
      null
    }
  }

  def run() = {
    // Process requests
    var request: Map[String, Any] = null
    while ({request = IO.receive[Map[String, Any]](); request} != null) {
      try {
        var response: Any = null
        if (!request.contains("tasks")) {
          response = executeFunction(request)
        } else {
          response = executeBatch(request)
        }

        IO.send(response)
      }
    }

    disconnect()
  }
}
