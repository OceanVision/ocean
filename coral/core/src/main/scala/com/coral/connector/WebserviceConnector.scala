package com.coral.connector

import java.net.ServerSocket
import akka.actor.{Props, ActorSystem}
import akka.routing.RoundRobinPool
import com.typesafe.config.ConfigFactory
import com.coral.workers._
import com.coral.messages.Connection
import com.coral.utils.Config

object WebserviceConnector extends Runnable {
  private val port = Config.webserviceConnectorPort

  // Creates cache workers
  private val cacheWorkerSystem = ActorSystem(
    "cacheWorkerSystem", ConfigFactory.load("cacheWorkerSystem"))
  private val cacheWorkerPool = cacheWorkerSystem.actorOf(
    Props(new CacheWorker).withRouter(
      RoundRobinPool(Config.numberOfCacheWorkers)), "cacheWorkerPool")
  println("Starting " + Config.numberOfCacheWorkers + " cache workers.")

  // Creates database workers
  private val databaseWorkerSystem = ActorSystem(
    "databaseWorkerSystem", ConfigFactory.load("databaseWorkerSystem"))
  private val databaseWorkerPool = databaseWorkerSystem.actorOf(
    Props(new DatabaseWorker).withRouter(
      RoundRobinPool(Config.numberOfDatabaseWorkers)), "databaseWorkerPool")
  println("Starting " + Config.numberOfDatabaseWorkers + " database workers.")

  // Creates session worker
  private val sessionWorkerSystem = ActorSystem(
    "sessionWorkerSystem", ConfigFactory.load("sessionWorkerSystem"))
  private val sessionWorker = sessionWorkerSystem.actorOf(Props(new SessionWorker), "sessionWorker")
  println("Starting session worker.")

  // Creates master worker
  private val masterSystem = ActorSystem(
    "masterSystem", ConfigFactory.load("masterSystem"))
  private val master = masterSystem.actorOf(Props(new Master), "master")
  println("Starting master.")

  // Creates request handlers
  private val requestHandlerSystem = ActorSystem("requestHandlerSystem")
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props(new RequestHandler(master)).withRouter(
      RoundRobinPool(Config.numberOfRequestHandlers)), "requestHandlerPool")
  println("Starting " + Config.numberOfRequestHandlers + " request handlers.")

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
