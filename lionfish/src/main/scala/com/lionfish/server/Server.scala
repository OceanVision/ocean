package com.lionfish.server

import java.net.ServerSocket
import scala.concurrent.Lock

object Server extends Runnable {
  private val port = 21
  private var dynamicId = 0
  private val threadLock = new Lock
  val availabilityLock = new Lock
  availabilityLock.acquire()

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

  def run() = {
    if (threadLock.available) {
      threadLock.acquire()

      try {
        val serverSocket = new ServerSocket(port)
        println(s"The Lionfish server is listening on port $port.")
        availabilityLock.release()
        handleConnections(serverSocket)
        serverSocket.close()
      } catch {
        case e: Exception => {
          println(s"Failed to start the Lionfish server. Error message: $e")
        }
      } finally {
        threadLock.release()
        println("The Lionfish server terminated.")
      }
    }
  }
}
