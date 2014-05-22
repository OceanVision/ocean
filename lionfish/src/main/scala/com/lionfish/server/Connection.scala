package com.lionfish.server

import java.net.Socket
import java.util.UUID
import scala.concurrent.Await
import scala.concurrent.duration._
import akka.actor._
import akka.util.Timeout
import akka.pattern.ask
import com.lionfish.utils.IO
import com.lionfish.messages.Request

class Connection(private val master: ActorRef)(private implicit val socket: Socket) extends Runnable {
  private implicit val timeout = Timeout(600 seconds)
  private val connectionUuid = UUID.randomUUID().toString

  private def disconnect() = {
    try {
      socket.close()
    } catch {
      case e: Exception => {
        println(s"Connection failed to disconnect. Error message: $e")
      }
    }
  }

  def run() = {
    // Process requests
    var request: Map[String, Any] = null
    while ({request = IO.receive[Map[String, Any]](); request} != null) {
      try {
        val future = master ? Request(connectionUuid, request)
        val response = Await.result[Any](future, timeout.duration)
        IO.send(response)
      }
    }

    disconnect()
  }
}
