package com.coral.connector

import java.net.Socket
import java.util.UUID
import akka.actor._
import com.coral.utils.IO
import com.coral.messages._

class RequestHandler(private val master: ActorRef) extends Actor {
  private val uuid = UUID.randomUUID().toString
  private implicit var socket: Socket = null

  def handle(id: Int) = {
    // Process request
    println(s"Processing request $id.")
    val request = IO.receive[Map[String, Any]]()
    master ! Request(uuid, request)
  }

  def receive = {
    case Connection(id, newSocket) => {
      socket = newSocket
      handle(id)
    }
    case Result(_, result) => {
      IO.send(result)
    }
  }
}
