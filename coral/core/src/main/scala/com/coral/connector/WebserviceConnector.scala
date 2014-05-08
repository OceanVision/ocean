package com.coral.connector

import java.net.ServerSocket

object WebserviceConnector extends Runnable {
  private val port = 7777
  private var dynamicId = 0

  private def getNewId: Int = {
    dynamicId += 1
    dynamicId
  }

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      val newId = getNewId
      new Thread(new RequestHandler(newId, socket)).start()
    }
  }

  def run() = {
    try {
      val serverSocket = new ServerSocket(port)
      println(s"The Coral webservice connector is listening on port $port.")
      handleConnections(serverSocket)
      serverSocket.close()
    } catch {
      case e: Exception => {
        println(s"Failed to start the Coral webservice connector. Error message: $e")
      }
    } finally {
      println("The Coral webservice connector terminated.")
    }
  }
}
