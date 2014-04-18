package lionfish.server
import java.net.ServerSocket
import rapture.json.jsonParsers
import jsonParsers.scalaJson._
import lionfish.server.{Connection, DatabaseManager}

object Server {
  private val port = 21
  private val manager = new DatabaseManager
  private var dynamicId = 0

  private def getNewId: Int = {
    dynamicId += 1
    dynamicId
  }

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      val newId = getNewId
      new Thread(new Connection(newId, socket, manager)).start()
    }
  }

  def start() = {
    try {
      val serverSocket = new ServerSocket(port)
      println(s"The server is listening on port $port.")
      handleConnections(serverSocket)
    } catch {
      case e: Exception => {
        println(s"Starting server failed.")
      }
    }
  }

  def main(args: Array[String]) = {
    start()
  }
}
