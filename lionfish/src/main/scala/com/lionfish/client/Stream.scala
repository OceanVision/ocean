package com.lionfish.client

import java.util.UUID
import akka.actor._
import akka.remote._

trait Stream {
  protected val streamSystem: ActorSystem
  protected val proxyAddress: String
  protected val proxyPort: Int

  // Connects to proxy
  protected val proxyPath = s"akka.tcp://proxySystem@$proxyAddress:$proxyPort/user/proxy"
  protected implicit val proxy = streamSystem.actorSelection(proxyPath)

  protected implicit val streamUuid = UUID.randomUUID().toString

  protected var macroMethod: Method = null

  def <<(method: Method) = {
    if (macroMethod == null) {
      macroMethod = method
    } else {
      macroMethod << method
    }
  }

  def !!(method: Method): Any

  def execute(): Any

  def receive = null
}
