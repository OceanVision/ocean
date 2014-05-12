package com.lionfish.server

import java.net.ServerSocket
//import akka.actor._
import scala.concurrent.Lock

object Server extends Runnable {
  private val port = 21
  private var dynamicId = 0
  private val threadLock = new Lock
  val availabilityLock = new Lock
  availabilityLock.acquire()

  private def getConnectionId: Int = {
    dynamicId += 1
    dynamicId
  }

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      val newId = getConnectionId
      new Thread(new RequestHandler(newId, socket)).start()
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
