package com.lionfish.server

import java.net.ServerSocket
import scala.concurrent.Lock
import akka.actor.{ActorSystem, Props}
import com.lionfish.utils.Config

object Server extends Runnable {
  var port = Config.defaultServerPort
  private val threadLock = new Lock
  val debugLock = new Lock
  debugLock.acquire()

  // Creates master worker
  private val masterSystem = ActorSystem("masterSystem")
  private val master = masterSystem.actorOf(Props(new Master))

  private def handleConnections(serverSocket: ServerSocket) = {
    while (true) {
      implicit val socket = serverSocket.accept()
      new Thread(new Connection(master)).start()
    }
  }

  def run() = {
    if (threadLock.available) {
      threadLock.acquire()

      try {
        val serverSocket = new ServerSocket(port)
        debugLock.release()
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
