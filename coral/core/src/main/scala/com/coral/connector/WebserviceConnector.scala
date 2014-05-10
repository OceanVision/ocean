package com.coral.connector

import java.net.ServerSocket
import akka.actor.{ActorSystem, ActorRef, Props}
import akka.routing.RoundRobinPool
import com.coral.actors.Master
import com.coral.messages.Connection

// TODO: I discovered that tcp server can be replaced with pykka <-> akka connectivity
// TODO: Use akka configuration!

object WebserviceConnector extends Runnable {
  private val port = 7777
  private var dynamicId = 0

  // Creates master worker
  private val masterSystem = ActorSystem("masterSystem")
  private val master = masterSystem.actorOf(Props(new Master), "master")

  private val requestHandlerSystem = ActorSystem("requestHandlerSystem")
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props(new RequestHandler(master)).withRouter(RoundRobinPool(10)), "requestHandlerPool")

  private def getConnectionId: Int = {
    dynamicId += 1
    dynamicId
  }

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      requestHandlerPool ! Connection(getConnectionId, socket)
    }
  }

  def run() = {
    try {
      // Initialises socket
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
