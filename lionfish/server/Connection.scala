package lionfish
import java.net.Socket
import java.nio.ByteBuffer
import rapture.io._
import strategy.throwExceptions
import lionfish.DatabaseManager

class Connection(private val id: Int,
                 private val socket: Socket,
                 private val manager: DatabaseManager) extends Runnable {
  val inputStream = socket.getInputStream
  val outputStream = socket.getOutputStream
  println(s"Client $id connected.")

  private def disconnect() = {
    try {
      socket.close()
      println(s"Client $id disconnected.")
    } catch {
      case e: Exception => {
        println(s"Client $id: disconnecting with client $id failed. Error message: $e")
      }
    }
  }

  // Sends a message to socket
  private def send(rawData: Any) = {
    try {
      // Serializes the data
      val serialisedMsg = Json.serialize(json"${rawData}")

      // Prepares length of a outcoming array
      val byteBuffer = ByteBuffer.allocate(4)
      byteBuffer.putInt(serialisedMsg.length)
      val msgLength = byteBuffer.array()

      // Prepares a certain message
      val msg: Array[Byte] = msgLength ++ serialisedMsg.getBytes
      outputStream.write(msg)
    } catch {
      case e: Exception => {
        println(s"Client $id: sending data to client $id failed. Error message: $e")
      }
    }
  }

  // Receives a message from socket
  private def receive(): Map[String, Any] = {
    try {
      // Gets length of a incoming message
      var readBuffer = new Array[Byte](4)
      var count = inputStream.read(readBuffer, 0, 4)

      if (count == -1) {
        return null
      }

      val dataLength: Int = ByteBuffer.wrap(readBuffer).getInt()
      var msg: String = ""

      // Gets a certain message
      readBuffer = new Array[Byte](dataLength)
      var totalCount = 0
      count = 0
      while (totalCount < dataLength) {
        count = inputStream.read(readBuffer, 0, dataLength)
        totalCount += count
        msg += new String(readBuffer, 0, count)
      }

      // Parses msg to data
      val data = Json.parse(msg).get[Map[String, Any]]
      data
    } catch {
      case e: Exception => {
        println(s"Client $id: receiving data from client $id failed. Error message: $e")
      }

      null
    }
  }

  private def executeFunction(request: Map[String, Any]): Any = {
    try {
      val funcName = request("funcName").asInstanceOf[String]
      val args = request("args").asInstanceOf[List[Map[String, Any]]]

      println(s"Client $id: $funcName")

      // TODO: Solve this with reflection
      var response: Any = null
      funcName match {
        case "getModelNodes" => {
          response = manager.getModelNodes()
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
    while ({request = receive(); request} != null) {
      try {
        var response: Any = null
        if (!request.contains("tasks")) {
          response = executeFunction(request)
        }
        send(response)
      }
    }

    disconnect()
  }
}
