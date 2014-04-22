package lionfish.server
import java.net.ServerSocket

object Server {
  private val port = 21
  private var dynamicId = 0

  private def getNewId: Int = {
    dynamicId += 1
    dynamicId
  }

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      val newId = getNewId
      new Thread(new Connection(newId, socket)).start()
    }
  }

  def start() = {
    try {
      val serverSocket = new ServerSocket(port)
      println(s"The Lionfish server is listening on port $port.")
      handleConnections(serverSocket)
    } catch {
      case e: Exception => {
        println(s"Failed to start the Lionfish server. Error message: $e")
      }
    }
  }

  def main(args: Array[String]) = {
    start()
  }
}
