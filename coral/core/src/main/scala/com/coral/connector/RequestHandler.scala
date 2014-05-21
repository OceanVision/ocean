package com.coral.connector

import java.net.Socket
import java.util.UUID
import akka.actor._
import com.coral.utils.IO
import com.coral.messages._

class RequestHandler(private val master: ActorRef) extends Actor {
  private val uuid = UUID.randomUUID().toString
  private implicit var socket: Socket = null

  def handle() = {
    // Processes request
    val request = IO.receive[Map[String, Any]]()
    master ! Request(uuid, request)
  }

  def receive = {
    case Connection(newSocket) => {
      socket = newSocket
      handle()
    }
    case Response(_, result) => {
      IO.send(result)
    }
  }
}
