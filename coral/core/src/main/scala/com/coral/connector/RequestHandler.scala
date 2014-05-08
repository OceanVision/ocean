package com.coral.connector

import java.net.Socket
import com.coral.utils.IO

class RequestHandler(private val id: Int, private implicit val socket: Socket) extends Runnable {
  private def disconnect() = {
    try {
      socket.close()
    } catch {
      case e: Exception => {
        println(s"Request $id handler failed to disconnect. Error message: $e")
      }
    }
  }

  private def execute(request: Map[String, Any]): Any = {
    // TODO: implementation
    println(s"request: $request")

    val result: Map[String, Any] = Map("stub" -> true)
    result
  }

  def run() = {
    // Process requests
    var request: Map[String, Any] = null
    println(s"Processing request $id.")
    while ({request = IO.receive[Map[String, Any]](); request} != null) {
      try {
        val response: Any = execute(request)
        IO.send(response)
      }
    }

    disconnect()
  }
}
