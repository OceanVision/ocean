package com.coral.connector

import java.net.ServerSocket
import akka.actor.{Props, ActorSystem}
import akka.routing.RoundRobinPool
import com.typesafe.config.ConfigFactory
import com.coral.workers._
import com.coral.messages.Connection

object WebserviceConnector extends Runnable {
  private val port = 7778

  // Creates database workers
  private val databaseWorkerSystem = ActorSystem(
    "databaseWorkerSystem", ConfigFactory.load("databaseWorkerSystem"))
  private val databaseWorkerPool = databaseWorkerSystem.actorOf(
    Props(new DatabaseWorker).withRouter(RoundRobinPool(10)), "databaseWorkerPool")

  // Creates session worker
  private val sessionWorkerSystem = ActorSystem(
    "sessionWorkerSystem", ConfigFactory.load("sessionWorkerSystem"))
  private val sessionWorker = sessionWorkerSystem.actorOf(Props(new SessionWorker), "sessionWorker")

  // Creates master worker
  private val masterSystem = ActorSystem(
    "masterSystem", ConfigFactory.load("masterSystem"))
  private val master = masterSystem.actorOf(Props(new Master), "master")

  // Creates request handlers
  private val requestHandlerSystem = ActorSystem("requestHandlerSystem")
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props(new RequestHandler(master)).withRouter(RoundRobinPool(10)), "requestHandlerPool")

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      requestHandlerPool ! Connection(socket)
    }
  }

  def run() = {
    try {
      // Initialises socket
      val serverSocket = new ServerSocket(port)

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
