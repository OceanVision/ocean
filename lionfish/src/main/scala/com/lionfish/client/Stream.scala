package com.lionfish.client

import java.net.Socket
import com.lionfish.utils.IO

trait Stream {
  protected val host = "localhost" // TODO: create a config file
  protected val port = 21
  protected implicit val socket: Socket = new Socket(host, port)
  protected var macroMethod: Method = null

  def disconnect() = {
    try {
      socket.close()
    } catch {
      case e: Exception => {
        println(s"Failed to disconnect with Lionfish server. Error message: $e")
      }
    }
  }

  def send(rawData: Any) = {
    IO.send(rawData)
  }

  def receive[T: Manifest](): T = {
    IO.receive[T]()
  }

  def <<(method: Method) = {
    if (macroMethod == null) {
      macroMethod = method
    } else {
      macroMethod << method
    }
  }

  def !!(method: Method): Any

  def execute(): Any
}
