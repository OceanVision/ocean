package com.lionfish.workers

import java.net.Socket
import java.util.UUID
import scala.concurrent.Await
import scala.concurrent.duration._
import akka.actor._
import akka.util.Timeout
import akka.pattern.ask
import com.lionfish.utils.{Config, IO}
import com.lionfish.messages._
import com.lionfish.logging.Logging

class RequestHandler extends Actor {
  private val log = Logging
  private implicit val timeout = Timeout(600 seconds)
  private val masterSystemPort = Config.masterSystemPort

  // Master worker
  private val masterPath =
    s"akka.tcp://masterSystem@localhost:$masterSystemPort/user/master"
  private val master = context.actorSelection(masterPath)

  private def disconnect(connectionUuid: String, socket: Socket) = {
    try {
      log.info(s"Closing connection $connectionUuid.")
      socket.close()
    } catch {
      case e: Exception => {
        log.error(s"Connection failed to disconnect. Error message: $e")
      }
    }
  }

  def handleConnection(connectionUuid: String)(implicit socket: Socket) = {
    log.info(s"New connection $connectionUuid.")

    // Process requests
    var request: Map[String, Any] = null
    while ({request = IO.receive[Map[String, Any]](); request} != null) {
      try {
        val future = master ? Request(connectionUuid, request)
        val response = Await.result[Any](future, timeout.duration)
        IO.send(response)
      }
    }

    disconnect(connectionUuid, socket)
  }

  def receive = {
    case Connection(socket) => {
      val connectionUuid = UUID.randomUUID().toString
      handleConnection(connectionUuid)(socket)
    }
  }
}
