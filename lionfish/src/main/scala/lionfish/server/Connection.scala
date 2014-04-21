package lionfish.server
import java.net.Socket
import lionfish.utils.io

class Connection(private val id: Int,
                 private implicit val socket: Socket,
                 private val manager: DatabaseManager) extends Runnable {
  println(s"Client $id connected.")

  private def disconnect() = {
    try {
      socket.close()
      println(s"Client $id disconnected.")
    } catch {
      case e: Exception => {
        println(s"Failed to disconnect with client. Error message: $e")
      }
    }
  }

  private def executeBatch(request: Map[String, Any]): List[Any] = {
    try {
      val count = request("count").asInstanceOf[Double].toInt
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
            rawResult = manager.getByUuid(fullArgs)
          }
          case "getByLink" => {
            rawResult = manager.getByLink(fullArgs)
          }
          case "getModelNodes" => {
            rawResult = manager.getModelNodes()
          }
          case "createNodes" => {
            rawResult = manager.createNodes(fullArgs)
          }
          case "deleteNodes" => {
            rawResult = manager.deleteNodes(fullArgs)
          }
          case _ => throw new NoSuchMethodException(funcName)
        }

        if (rawResult != null) {
          for (i <- 0 to rawResult.length - 1) {
            response = response.updated(params(i)(1).asInstanceOf[Double].toInt, rawResult(i))
          }
        }
      }

      response
    } catch {
      case e: Exception => {
        println(s"Failed to execute batch. Error message: $e")
      }
      List()
    }
  }

  private def executeFunction(request: Map[String, Any]): List[Any] = {
    try {
      val funcName = request("funcName").asInstanceOf[String]
      val args = List(request("args").asInstanceOf[Map[String, Any]])

      println(s"Client $id executes $funcName.")

      // TODO: Solve this with reflection
      var response: List[Any] = null
      funcName match {
        case "getByUuid" => {
          response = manager.getByUuid(args)
        }
        case "getByLink" => {
          response = manager.getByLink(args)
        }
        case "getModelNodes" => {
          response = manager.getModelNodes()
        }
        case "createNodes" => {
          response = manager.createNodes(args)
        }
        case "deleteNodes" => {
          response = manager.deleteNodes(args)
        }
        case _ => throw new NoSuchMethodException(funcName)
      }

      response
    } catch {
      case e: Exception => {
        println(s"Client $id: executing function failed. Error message: $e")
      }
      List()
    }
  }

  def run() = {
    // Process requests
    var request: Map[String, Any] = null
    while ({request = io.receive[Map[String, Any]](); request} != null) {
      try {
        var response: List[Any] = null
        if (!request.contains("tasks")) {
          response = executeFunction(request)
        } else {
          response = executeBatch(request)
        }
        io.send(response)
      }
    }

    disconnect()
  }
}
