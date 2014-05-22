package com.lionfish.client

import java.net.Socket

trait Stream {
  protected val serverAddress: String
  protected val serverPort: Int

  // Connects to the server
  protected implicit val socket: Socket = new Socket(serverAddress, serverPort)
  protected var macroMethod: Method = null

  def close() = {
    socket.close()
  }

  def <<(method: Method): Stream = {
    if (macroMethod == null) {
      macroMethod = method
    } else {
      macroMethod << method
    }
    this
  }

  def !!(method: Method): Any

  def execute(): Any

  def receive = null
}
