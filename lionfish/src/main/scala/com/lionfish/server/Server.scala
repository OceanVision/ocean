package com.lionfish.server

import java.net.ServerSocket
import scala.concurrent.Lock
import akka.actor.{Props, ActorSystem}
import akka.routing.RoundRobinPool
import com.typesafe.config.ConfigFactory
import com.lionfish.utils.Config
import com.lionfish.messages.Connection
import com.lionfish.workers._
import com.lionfish.logging.Logging

object Server extends Runnable {
  private val log = Logging
  private val serverPort = Config.serverPort
  private val threadLock = new Lock
  val debugLock = new Lock
  debugLock.acquire()

  // Creates database workers
  private val databaseWorkerSystem = ActorSystem(
    "databaseWorkerSystem", ConfigFactory.load("databaseWorkerSystem"))
  private val databaseWorkerPool = databaseWorkerSystem.actorOf(
    Props(new DatabaseWorker).withRouter(
      RoundRobinPool(Config.numberOfDatabaseWorkers)), "databaseWorkerPool")
  log.info("Starting " + Config.numberOfDatabaseWorkers + " database workers.")

  // Creates cache workers
  private val cacheWorkerSystem = ActorSystem(
    "cacheWorkerSystem", ConfigFactory.load("cacheWorkerSystem"))
  private val cacheWorkerPool = cacheWorkerSystem.actorOf(
    Props(new CacheWorker).withRouter(
      RoundRobinPool(Config.numberOfCacheWorkers)), "cacheWorkerPool")
  log.info("Starting " + Config.numberOfCacheWorkers + " cache workers.")

  // Creates master worker
  private val masterSystem = ActorSystem(
    "masterSystem", ConfigFactory.load("masterSystem"))
  private val master = masterSystem.actorOf(Props(new Master), "master")
  log.info("Starting master.")

  // Creates request handlers
  private val requestHandlerSystem = ActorSystem(
    "requestHandlerSystem", ConfigFactory.load("requestHandlerSystem"))
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props(new RequestHandler).withRouter(
      RoundRobinPool(Config.numberOfRequestHandlers)), "requestHandlerPool")
  log.info("Starting " + Config.numberOfRequestHandlers + " request handlers.")

  // Handles incoming connections
  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      val socket = serverSocket.accept()
      requestHandlerPool ! Connection(socket)
    }
  }

  def run() = {
    if (threadLock.available) {
      threadLock.acquire()

      try {
        val serverSocket = new ServerSocket(serverPort)
        debugLock.release()
        handleConnections(serverSocket)
        serverSocket.close()
      } catch {
        case e: Exception => {
          log.error(s"Failed to start the Lionfish server. Error message: $e")
        }
      } finally {
        threadLock.release()
        log.info("The Lionfish server terminated.")
      }
    }
  }
}
