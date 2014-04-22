package lionfish.server
import java.net.Socket
import lionfish.utils.IO

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

        println(s"Client $id executes $funcName.")

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
          case "set" => {
            rawResult = DatabaseManager.set(fullArgs)
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
        println(s"Client $id failed to execute batch at line $line. Error message: $e")
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
        case "set" => {
          response = DatabaseManager.set(args)
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
        case _ => throw new NoSuchMethodException(funcName)
      }

      response(0)
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Client $id failed to execute function at line $line. Error message: $e")
      }
      List()
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
